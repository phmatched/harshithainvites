"""A small painterly rasteriser — pure stdlib, no Pillow, no numpy.

Flat vector shapes read as flat no matter how many you stack up. What makes an
image read as *painted* is a handful of specific things, and this module exists
to provide them:

  * soft brush dabs with per-dab colour jitter, so edges break up
  * atmospheric haze, so distance is felt rather than implied
  * one directional light, with warm light and cool (violet-shifted) shadow
  * contact shadows where objects meet the ground
  * additive bloom around anything that glows
  * gradient-shaded solids, so architecture sits *in* the scene

Everything accumulates into a float buffer and is quantised once at save time.
"""

import zlib, struct, math, random
from array import array


# ============================================================== PNG + helpers

def write_png(path, w, h, rgb, alpha=None):
    """8-bit RGB, or RGBA when `alpha` is given."""
    if alpha is None:
        raw = b"".join(b"\x00" + bytes(rgb[y * w * 3:(y + 1) * w * 3]) for y in range(h))
        ctype = 2
    else:
        rows = []
        for y in range(h):
            row = bytearray(b"\x00")
            for x in range(w):
                i = y * w + x
                j = i * 3
                row += bytes((rgb[j], rgb[j + 1], rgb[j + 2], alpha[i]))
            rows.append(bytes(row))
        raw = b"".join(rows)
        ctype = 6

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff))

    blob = (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, ctype, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9))
            + chunk(b"IEND", b""))
    open(path, "wb").write(blob)
    return len(blob)


def smooth(t):
    return t * t * (3 - 2 * t)


def _noise_grid(cx, cy, rng):
    return [[rng.random() for _ in range(cx + 1)] for _ in range(cy + 1)]


def _sample(grid, cx, cy, u, v):
    fx, fy = u * cx, v * cy
    x0, y0 = int(fx), int(fy)
    tx, ty = smooth(fx - x0), smooth(fy - y0)
    x1, y1 = min(x0 + 1, cx), min(y0 + 1, cy)
    a = grid[y0][x0] * (1 - tx) + grid[y0][x1] * tx
    b = grid[y1][x0] * (1 - tx) + grid[y1][x1] * tx
    return a * (1 - ty) + b * ty


def fbm_field(w, h, octaves, base, seed):
    """Fractal value noise in [0,1] as a flat list."""
    rng = random.Random(seed)
    layers, amp, cells, total = [], 1.0, base, 0.0
    for _ in range(octaves):
        layers.append((_noise_grid(cells, cells, rng), cells, amp))
        total += amp
        amp *= 0.5
        cells *= 2

    out = [0.0] * (w * h)
    for y in range(h):
        v = y / (h - 1) if h > 1 else 0.0
        row = y * w
        for x in range(w):
            u = x / (w - 1) if w > 1 else 0.0
            acc = 0.0
            for grid, cells, amp in layers:
                acc += _sample(grid, cells, cells, u, v) * amp
            out[row + x] = acc / total
    return out


def ramp(stops, t):
    """stops: [(pos, (r,g,b)), ...] ascending."""
    t = 0.0 if t < 0 else (1.0 if t > 1 else t)
    for i in range(len(stops) - 1):
        p0, c0 = stops[i]
        p1, c1 = stops[i + 1]
        if p0 <= t <= p1:
            k = 0 if p1 == p0 else smooth((t - p0) / (p1 - p0))
            return (c0[0] + (c1[0] - c0[0]) * k,
                    c0[1] + (c1[1] - c0[1]) * k,
                    c0[2] + (c1[2] - c0[2]) * k)
    return stops[-1][1]


def mix(a, b, k):
    k = 0.0 if k < 0 else (1.0 if k > 1 else k)
    return (a[0] + (b[0] - a[0]) * k,
            a[1] + (b[1] - a[1]) * k,
            a[2] + (b[2] - a[2]) * k)


def shade(base, amount):
    """Lighten (amount>0) or deepen-and-cool (amount<0).

    Real shadow is not just darker — it shifts cool. That single detail does
    more for believability than any amount of extra geometry.
    """
    if amount >= 0:
        return mix(base, (255, 248, 225), amount)          # warm light
    return mix(base, (34, 26, 58), -amount)                # violet shadow


# ============================================================== the canvas

_KERNELS = {}


def _kernel(r):
    """Radial falloff for one brush dab, cached per integer radius."""
    r = max(1, int(r))
    k = _KERNELS.get(r)
    if k is None:
        rows = []
        rr = float(r * r)
        for dy in range(-r, r + 1):
            row = []
            for dx in range(-r, r + 1):
                d2 = dx * dx + dy * dy
                if d2 >= rr:
                    row.append(0.0)
                else:
                    f = 1.0 - d2 / rr
                    row.append(f * f)          # soft, smooth shoulder
            rows.append(row)
        k = rows
        _KERNELS[r] = k
    return k


class Painting:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.buf = array("f", [0.0]) * (w * h * 3)
        self.a = array("f", [0.0]) * (w * h)

    # ---------------------------------------------------------- ground layers

    def sky(self, stops, warp_seed=1, warp=0.14, mottle=0.22):
        """A vertical ramp, warped by noise so bands never look mechanical."""
        w, h, buf, al = self.w, self.h, self.buf, self.a
        wf = fbm_field(w, h, 4, 2, warp_seed)
        mf = fbm_field(w, h, 5, 3, warp_seed + 77)
        for y in range(h):
            v = y / (h - 1)
            row = y * w
            for x in range(w):
                i = row + x
                c = ramp(stops, v + (wf[i] - 0.5) * warp)
                m = (mf[i] - 0.5) * mottle
                j = i * 3
                buf[j] = c[0] * (1 + m)
                buf[j + 1] = c[1] * (1 + m)
                buf[j + 2] = c[2] * (1 + m * 1.05)
                al[i] = 1.0

    def haze(self, y0, y1, rgb, strength):
        """Atmospheric band — the main depth cue in any landscape."""
        w, h, buf = self.w, self.h, self.buf
        y0 = max(0, int(y0)); y1 = min(h, int(y1))
        span = max(1, y1 - y0)
        r0, g0, b0 = rgb
        for y in range(y0, y1):
            t = 1.0 - (y - y0) / span
            k = strength * t * t
            if k <= 0.001:
                continue
            j = y * w * 3
            for _ in range(w):
                buf[j] += (r0 - buf[j]) * k
                buf[j + 1] += (g0 - buf[j + 1]) * k
                buf[j + 2] += (b0 - buf[j + 2]) * k
                j += 3

    # ---------------------------------------------------------- brushwork

    def dab(self, x, y, r, rgb, a=1.0):
        """One soft brush mark, painted over what is already there."""
        w, h, buf, al = self.w, self.h, self.buf, self.a
        r = max(1, int(r))
        ix, iy = int(x), int(y)
        x0, x1 = max(0, ix - r), min(w - 1, ix + r)
        y0, y1 = max(0, iy - r), min(h - 1, iy + r)
        if x0 > x1 or y0 > y1:
            return
        kern = _kernel(r)
        cr, cg, cb = rgb
        for py in range(y0, y1 + 1):
            krow = kern[py - iy + r]
            base = py * w
            for px in range(x0, x1 + 1):
                wt = krow[px - ix + r]
                if wt <= 0.0:
                    continue
                k = wt * a
                i = base + px
                j = i * 3
                buf[j] += (cr - buf[j]) * k
                buf[j + 1] += (cg - buf[j + 1]) * k
                buf[j + 2] += (cb - buf[j + 2]) * k
                if al[i] < 1.0:
                    al[i] += (1.0 - al[i]) * k

    def stroke(self, pts, r, rgb, a=1.0, step=None):
        """Dabs laid along a path."""
        step = step or max(1.0, r * 0.45)
        for i in range(len(pts) - 1):
            x0, y0 = pts[i]
            x1, y1 = pts[i + 1]
            d = math.hypot(x1 - x0, y1 - y0)
            n = max(1, int(d / step))
            for s in range(n + 1):
                t = s / n
                self.dab(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, r, rgb, a)

    def mass(self, cx, cy, rx, ry, rgb, n=260, dab_r=9, jitter=0.16,
             light=(-0.55, -0.8), seed=0, depth=0.0, sky_rgb=None, a=0.85):
        """A clump of dabs — this is how foliage, cloud and crowd get painted.

        `depth` in [0,1] pulls the clump toward `sky_rgb`, which is how distant
        masses lose contrast against the sky.
        """
        rng = random.Random(seed)
        lx, ly = light
        base = rgb
        if depth > 0 and sky_rgb:
            base = mix(base, sky_rgb, depth * 0.75)
        for _ in range(n):
            # a point inside the ellipse, denser toward the middle
            ang = rng.random() * math.tau
            rad = math.sqrt(rng.random())
            ox, oy = math.cos(ang) * rad, math.sin(ang) * rad
            px, py = cx + ox * rx, cy + oy * ry
            lit = (ox * lx + oy * ly)                      # -1 shadow .. +1 lit
            col = shade(base, lit * (0.30 - depth * 0.18))
            jf = 1.0 + (rng.random() - 0.5) * jitter
            col = (col[0] * jf, col[1] * jf, col[2] * jf)
            self.dab(px, py, dab_r * rng.uniform(0.65, 1.35), col,
                     a * rng.uniform(0.55, 1.0))

    # ---------------------------------------------------------- solids

    def poly(self, pts, rgb, light=(-0.6, -0.8), relief=0.30, seed=3, edge=True):
        """A scanline-filled solid, shaded across the light direction.

        Used for architecture. A flat fill would undo everything else.
        """
        w, h, buf, al = self.w, self.h, self.buf, self.a
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        bx0, bx1 = min(xs), max(xs)
        by0, by1 = min(ys), max(ys)
        bw = max(1.0, bx1 - bx0)
        bh = max(1.0, by1 - by0)
        lx, ly = light
        rng = random.Random(seed)
        grain = [rng.uniform(-0.035, 0.035) for _ in range(64)]

        y_start = max(0, int(math.floor(by0)))
        y_end = min(h - 1, int(math.ceil(by1)))
        n = len(pts)
        for py in range(y_start, y_end + 1):
            yc = py + 0.5
            xs_hit = []
            for i in range(n):
                ax, ay = pts[i]
                bx, byy = pts[(i + 1) % n]
                if (ay <= yc < byy) or (byy <= yc < ay):
                    xs_hit.append(ax + (yc - ay) / (byy - ay) * (bx - ax))
            if not xs_hit:
                continue
            xs_hit.sort()
            for k in range(0, len(xs_hit) - 1, 2):
                px0 = max(0, int(math.ceil(xs_hit[k])))
                px1 = min(w - 1, int(math.floor(xs_hit[k + 1])))
                if px1 < px0:
                    continue
                run = max(1.0, xs_hit[k + 1] - xs_hit[k])
                for px in range(px0, px1 + 1):
                    u = (px - bx0) / bw
                    v = (py - by0) / bh
                    t = (u - 0.5) * lx + (v - 0.5) * ly          # -1 .. +1
                    amt = t * relief + grain[(px * 7 + py * 13) & 63]
                    col = shade(rgb, amt)
                    if edge:
                        # catch the light along the leading edge
                        e = (px - xs_hit[k]) / run
                        if e < 0.09:
                            col = shade(col, 0.26 * (1 - e / 0.09))
                        elif e > 0.93:
                            col = shade(col, -0.20 * ((e - 0.93) / 0.07))
                    i2 = py * w + px
                    j = i2 * 3
                    buf[j] = col[0]
                    buf[j + 1] = col[1]
                    buf[j + 2] = col[2]
                    al[i2] = 1.0

    def rect(self, x, y, rw, rh, rgb, **kw):
        self.poly([(x, y), (x + rw, y), (x + rw, y + rh), (x, y + rh)], rgb, **kw)

    # ---------------------------------------------------------- light & shade

    def glow(self, x, y, r, rgb, strength=0.8):
        """Additive bloom. Anything with a flame needs this."""
        w, h, buf = self.w, self.h, self.buf
        r = int(r)
        x0, x1 = max(0, int(x) - r), min(w - 1, int(x) + r)
        y0, y1 = max(0, int(y) - r), min(h - 1, int(y) + r)
        rr = float(r * r)
        gr, gg, gb = rgb
        for py in range(y0, y1 + 1):
            dy = py - y
            base = py * w
            for px in range(x0, x1 + 1):
                dx = px - x
                d2 = dx * dx + dy * dy
                if d2 >= rr:
                    continue
                f = 1.0 - d2 / rr
                k = f * f * strength
                j = (base + px) * 3
                buf[j] = min(255.0, buf[j] + gr * k)
                buf[j + 1] = min(255.0, buf[j + 1] + gg * k)
                buf[j + 2] = min(255.0, buf[j + 2] + gb * k)

    def shadow(self, cx, cy, rx, ry, strength=0.45):
        """A soft contact shadow — what actually seats an object on the ground."""
        w, h, buf = self.w, self.h, self.buf
        x0, x1 = max(0, int(cx - rx)), min(w - 1, int(cx + rx))
        y0, y1 = max(0, int(cy - ry)), min(h - 1, int(cy + ry))
        for py in range(y0, y1 + 1):
            dy = (py - cy) / max(1.0, ry)
            base = py * w
            for px in range(x0, x1 + 1):
                dx = (px - cx) / max(1.0, rx)
                d2 = dx * dx + dy * dy
                if d2 >= 1.0:
                    continue
                f = 1.0 - d2
                k = f * f * strength
                j = (base + px) * 3
                buf[j] += (26.0 - buf[j]) * k
                buf[j + 1] += (20.0 - buf[j + 1]) * k
                buf[j + 2] += (44.0 - buf[j + 2]) * k

    # ---------------------------------------------------------- finishing

    def vignette(self, strength=0.22):
        w, h, buf = self.w, self.h, self.buf
        cx, cy = w / 2.0, h / 2.0
        maxd = math.hypot(cx, cy)
        for y in range(h):
            base = y * w
            for x in range(w):
                d = math.hypot(x - cx, y - cy) / maxd
                k = max(0.0, (d - 0.55) / 0.45) ** 2 * strength
                if k <= 0.001:
                    continue
                j = (base + x) * 3
                buf[j] *= (1 - k)
                buf[j + 1] *= (1 - k)
                buf[j + 2] *= (1 - k * 0.92)

    def grain(self, amount=0.022, seed=5):
        rng = random.Random(seed)
        buf = self.buf
        for j in range(0, len(buf), 3):
            g = (rng.random() - 0.5) * 255 * amount
            buf[j] += g
            buf[j + 1] += g
            buf[j + 2] += g * 0.94

    def fade_top(self, frac=0.20, curve=1.6):
        """Ramp alpha in from the top, so the painting composites onto whatever
        sky sits behind it instead of showing a hard upper edge."""
        w, h, al = self.w, self.h, self.a
        cut = max(1, int(h * frac))
        for y in range(cut):
            k = (y / cut) ** curve
            base = y * w
            for x in range(w):
                al[base + x] *= k

    def save(self, path, rgba=False):
        w, h = self.w, self.h
        buf, al = self.buf, self.a
        out = bytearray(w * h * 3)
        for j in range(len(buf)):
            v = buf[j]
            out[j] = 0 if v < 0 else (255 if v > 255 else int(v))
        if rgba:
            aout = bytearray(w * h)
            for i in range(w * h):
                v = al[i] * 255.0
                aout[i] = 0 if v < 0 else (255 if v > 255 else int(v))
            size = write_png(path, w, h, out, aout)
        else:
            size = write_png(path, w, h, out)
        print("  %-24s %5dx%-5d %7.1f KB" % (path.split("/")[-1], w, h, size / 1024))
        return size
