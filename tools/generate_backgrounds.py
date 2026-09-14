"""Paint the watercolour background washes and paper grain.

Pure stdlib. Washes are generated small (soft, low-frequency content upscales
cleanly) so the files stay light for phones on mobile data. High-frequency
grain ships separately as a tiny tileable overlay.
"""
import zlib, struct, math, random

OUT = "/Users/prathik/Documents/InvitationAshu/assets/img/"


# ---------------------------------------------------------------- PNG writer
def write_png(path, w, h, rgb, alpha=None):
    if alpha is None:
        raw = b"".join(b"\x00" + bytes(rgb[y * w * 3:(y + 1) * w * 3]) for y in range(h))
        ctype = 2
    else:
        rows = []
        for y in range(h):
            row = bytearray(b"\x00")
            for x in range(w):
                i = (y * w + x) * 3
                row += bytes((rgb[i], rgb[i + 1], rgb[i + 2], alpha[y * w + x]))
            rows.append(bytes(row))
        raw = b"".join(rows)
        ctype = 6

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff))

    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, ctype, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9))
           + chunk(b"IEND", b""))
    open(path, "wb").write(png)
    return len(png)


# ---------------------------------------------------------------- noise
def noise_grid(cells_x, cells_y, rng):
    return [[rng.random() for _ in range(cells_x + 1)] for _ in range(cells_y + 1)]


def smooth(t):
    return t * t * (3 - 2 * t)


def sample(grid, cx, cy, u, v):
    """Bilinear sample of a cell grid at normalised (u, v)."""
    fx, fy = u * cx, v * cy
    x0, y0 = int(fx), int(fy)
    tx, ty = smooth(fx - x0), smooth(fy - y0)
    x1, y1 = min(x0 + 1, cx), min(y0 + 1, cy)
    a = grid[y0][x0] * (1 - tx) + grid[y0][x1] * tx
    b = grid[y1][x0] * (1 - tx) + grid[y1][x1] * tx
    return a * (1 - ty) + b * ty


def fbm_field(w, h, octaves, base, seed):
    """Fractal value noise in [0,1], returned as a flat list."""
    rng = random.Random(seed)
    layers = []
    amp, cells = 1.0, base
    total = 0.0
    for _ in range(octaves):
        layers.append((noise_grid(cells, cells, rng), cells, amp))
        total += amp
        amp *= 0.5
        cells *= 2

    out = [0.0] * (w * h)
    for y in range(h):
        v = y / (h - 1)
        for x in range(w):
            u = x / (w - 1)
            acc = 0.0
            for grid, cells, amp in layers:
                acc += sample(grid, cells, cells, u, v) * amp
            out[y * w + x] = acc / total
    return out


# ---------------------------------------------------------------- colour
def ramp(stops, t):
    """stops: [(pos, (r,g,b)), ...] sorted by pos."""
    t = max(0.0, min(1.0, t))
    for i in range(len(stops) - 1):
        p0, c0 = stops[i]
        p1, c1 = stops[i + 1]
        if p0 <= t <= p1:
            k = 0 if p1 == p0 else (t - p0) / (p1 - p0)
            k = smooth(k)
            return tuple(c0[j] + (c1[j] - c0[j]) * k for j in range(3))
    return stops[-1][1]


def mix(a, b, k):
    k = max(0.0, min(1.0, k))
    return tuple(a[j] + (b[j] - a[j]) * k for j in range(3))


def paint_wash(path, w, h, stops, blooms, seed, grain=0.012):
    """A vertical gradient, warped and mottled like pigment on wet paper."""
    warp = fbm_field(w, h, 4, 2, seed)
    mottle = fbm_field(w, h, 5, 3, seed + 101)
    rng = random.Random(seed + 7)

    rgb = bytearray(w * h * 3)
    for y in range(h):
        v = y / (h - 1)
        for x in range(w):
            i = y * w + x
            # let the gradient wander so bands never look mechanical
            t = v + (warp[i] - 0.5) * 0.16
            c = ramp(stops, t)

            # watercolour blooms
            for (bx, by, br, bc, bs) in blooms:
                d = math.hypot((x / w - bx) * (w / h), y / h - by) / br
                d += (mottle[i] - 0.5) * 0.55          # ragged, wet edges
                if d < 1.0:
                    c = mix(c, bc, (1 - d) ** 2 * bs)

            # pigment granulation
            c = mix(c, (c[0] * .86, c[1] * .86, c[2] * .88), (mottle[i] - 0.5) * 0.30)

            g = (rng.random() - 0.5) * 255 * grain
            j = i * 3
            rgb[j]     = max(0, min(255, int(c[0] + g)))
            rgb[j + 1] = max(0, min(255, int(c[1] + g)))
            rgb[j + 2] = max(0, min(255, int(c[2] + g)))

    size = write_png(path, w, h, rgb)
    print("  %-22s %5dx%-5d %7.1f KB" % (path.split("/")[-1], w, h, size / 1024))


# ---------------------------------------------------------------- grain tile
def paint_grain(path, n=160, seed=99):
    """Seamless handmade-paper fibre, as a transparent overlay."""
    rng = random.Random(seed)
    rgb = bytearray(n * n * 3)
    alpha = bytearray(n * n)
    for y in range(n):
        for x in range(n):
            i = y * n + x
            f = rng.random()
            # a few long fibres
            fib = 1.0 if rng.random() < 0.0016 else 0.0
            val = f * 0.55 + fib * 0.45
            dark = val < 0.5
            c = 90 if dark else 255
            rgb[i * 3] = rgb[i * 3 + 1] = rgb[i * 3 + 2] = c
            alpha[i] = int(abs(val - 0.5) * 2 * 26 + fib * 22)
    size = write_png(path, n, n, rgb, alpha)
    print("  %-22s %5dx%-5d %7.1f KB" % (path.split("/")[-1], n, n, size / 1024))


# ---------------------------------------------------------------- go
IVORY   = (250, 244, 231)
CHAMP   = (246, 233, 210)
BLUSH   = (243, 218, 205)
APRICOT = (240, 208, 176)
GOLDEN  = (233, 194, 143)
SAND    = (226, 182, 132)
ROSE    = (226, 170, 166)
SAGE    = (198, 206, 176)

MAROON   = (124, 31, 26)
MAR_DEEP = (72, 16, 14)
MAR_LIT  = (150, 52, 42)
GOLD     = (201, 162, 39)

print("painting backgrounds...")

# Hero: dawn sky over a temple garden — ivory at top, warm gold low down.
paint_wash(
    OUT + "wash-hero.png", 520, 780,
    [(0.00, IVORY), (0.18, CHAMP), (0.42, BLUSH), (0.68, APRICOT), (0.88, GOLDEN), (1.00, SAND)],
    blooms=[
        (0.20, 0.26, 0.34, ROSE,  0.42),
        (0.82, 0.34, 0.30, ROSE,  0.34),
        (0.50, 0.62, 0.40, GOLDEN, 0.40),
        (0.12, 0.76, 0.30, SAGE,  0.28),
        (0.88, 0.80, 0.28, SAGE,  0.24),
    ],
    seed=11)

# Soft cream for the body sections.
paint_wash(
    OUT + "wash-cream.png", 420, 560,
    [(0.00, IVORY), (0.50, (252, 247, 237)), (1.00, CHAMP)],
    blooms=[
        (0.25, 0.30, 0.40, BLUSH, 0.22),
        (0.78, 0.70, 0.38, CHAMP, 0.30),
    ],
    seed=23, grain=0.008)

# Deep maroon for the closing section.
paint_wash(
    OUT + "wash-deep.png", 460, 620,
    [(0.00, MAR_LIT), (0.35, MAROON), (1.00, MAR_DEEP)],
    blooms=[
        (0.50, 0.18, 0.45, MAR_LIT, 0.55),
        (0.18, 0.72, 0.34, GOLD,    0.10),
        (0.84, 0.66, 0.32, GOLD,    0.09),
    ],
    seed=37, grain=0.010)

paint_grain(OUT + "grain.png")
print("done.")
