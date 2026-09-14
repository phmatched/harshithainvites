"""Draw the ornament library as SVG.

Generated rather than hand-written: torans, mandalas and cusped arches are
repetition with controlled variation, which is exactly what a script is for.
Every piece is pure vector, so it stays crisp at any size and weighs almost
nothing.
"""
import math, random

OUT = "/Users/prathik/Documents/InvitationAshu/assets/img/"

# ---------------------------------------------------------------- palette
GOLD_D, GOLD, GOLD_L, GOLD_P = "#9A711A", "#C9A227", "#E3CC8A", "#F2E4BE"
MARI_D, MARI, MARI_L, MARI_P = "#C4660A", "#EE8E10", "#F7B23E", "#FFD375"
LEAF_D, LEAF, LEAF_L = "#2C5330", "#3F7340", "#5E9455"
ROSE_D, ROSE, ROSE_L, ROSE_P = "#B44E5E", "#D2788A", "#E7A6B2", "#F6D3D8"
CREAM, SHELL = "#FFFBF2", "#E6D8B8"
TEAL_D, TEAL, TEAL_L, BLUE_D = "#0B5C60", "#118087", "#2AA8A8", "#123E6E"


def svg(w, h, body, defs=""):
    d = "<defs>%s</defs>" % defs if defs else ""
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %g %g" fill="none">\n%s%s\n</svg>\n'
            % (w, h, d, body))


def save(name, content):
    open(OUT + name, "w").write(content)
    print("  %-22s %7.1f KB" % (name, len(content) / 1024))


def rot(a, cx, cy):
    return 'transform="rotate(%.1f %.1f %.1f)"' % (math.degrees(a) + 90, cx, cy)


# ================================================================ primitives
def petal_ring(cx, cy, r, n, col, spread, rx_f, ry_f, phase=0.0):
    """A ring of rotated-ellipse petals facing outward."""
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n + phase
        px, py = cx + math.cos(a) * r * spread, cy + math.sin(a) * r * spread
        out.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" %s/>'
                   % (px, py, r * rx_f, r * ry_f, col, rot(a, px, py)))
    return "".join(out)


def marigold_def(r=10):
    """Marigold drawn once at the origin; instances are <use> + scale."""
    out = []
    for ri, (sc, n, col) in enumerate([(1.0, 13, MARI_D), (0.80, 11, MARI),
                                       (0.58, 9, MARI_L), (0.34, 7, MARI_P)]):
        rr = r * sc
        for i in range(n):
            a = 2 * math.pi * i / n + ri * 0.42
            out.append('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="%s"/>'
                       % (math.cos(a) * rr * 0.60, math.sin(a) * rr * 0.60, rr * 0.46, col))
    out.append('<circle cx="0" cy="0" r="%.2f" fill="%s"/>' % (r * 0.17, MARI_P))
    return '<g id="mari">%s</g>' % "".join(out)


def use_mari(x, y, r):
    return '<use href="#mari" transform="translate(%.1f %.1f) scale(%.3f)"/>' % (x, y, r / 10.0)


def leaf(cx, cy, length, angle_deg, col=LEAF, vein=LEAF_D):
    a = math.radians(angle_deg)
    tx, ty = cx + math.cos(a) * length, cy + math.sin(a) * length
    wx, wy = -math.sin(a) * length * 0.28, math.cos(a) * length * 0.28
    mx, my = cx + math.cos(a) * length * 0.45, cy + math.sin(a) * length * 0.45
    return ('<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f Q%.1f %.1f %.1f %.1f Z" fill="%s"/>'
            '<path d="M%.1f %.1f L%.1f %.1f" stroke="%s" stroke-width="%.1f" opacity=".45"/>'
            % (cx, cy, mx + wx, my + wy, tx, ty, mx - wx, my - wy, cx, cy, col,
               cx, cy, tx, ty, vein, max(0.6, length * 0.03)))


def rose(cx, cy, r, seed=0):
    """Layered petals spiralling to a coiled centre — reads as a garden rose."""
    rng = random.Random(seed)
    out = [ '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (cx, cy, r * 0.92, ROSE_D) ]
    out.append(petal_ring(cx, cy, r, 7, ROSE_D, 0.50, 0.40, 0.54, rng.uniform(0, 1)))
    out.append(petal_ring(cx, cy, r * 0.78, 6, ROSE, 0.48, 0.42, 0.56, rng.uniform(0, 1)))
    out.append(petal_ring(cx, cy, r * 0.55, 5, ROSE_L, 0.46, 0.44, 0.58, rng.uniform(0, 1)))
    out.append(petal_ring(cx, cy, r * 0.34, 4, ROSE_P, 0.42, 0.46, 0.60, rng.uniform(0, 1)))
    # the coil at the heart
    out.append('<path d="M%.1f %.1f a%.1f %.1f 0 1 1 -%.1f -%.1f" stroke="%s" '
               'stroke-width="%.1f" fill="none" stroke-linecap="round" opacity=".75"/>'
               % (cx + r * 0.17, cy, r * 0.17, r * 0.17, r * 0.17, r * 0.17, ROSE_D,
                  max(0.9, r * 0.08)))
    return "".join(out)


def jasmine(cx, cy, r):
    out = [petal_ring(cx, cy, r, 5, CREAM, 0.55, 0.42, 0.60, -0.4)]
    out.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (cx, cy, r * 0.22, MARI_P))
    return "".join(out)


def bud(cx, cy, r, angle_deg, col=ROSE):
    """A closed bud: teardrop petal sitting in a green calyx."""
    a = math.radians(angle_deg)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux                       # perpendicular
    tipx, tipy = cx + ux * r * 2.0, cy + uy * r * 2.0
    return (
        # calyx
        '<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f Q%.1f %.1f %.1f %.1f Z" fill="%s"/>'
        # petal
        '<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f Q%.1f %.1f %.1f %.1f Z" fill="%s"/>'
        '<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f" stroke="%s" stroke-width="%.1f" fill="none" opacity=".45"/>'
        % (cx, cy,
           cx + px * r * 0.95, cy + py * r * 0.95, cx + ux * r * 1.0, cy + uy * r * 1.0,
           cx - px * r * 0.95, cy - py * r * 0.95, cx, cy, LEAF_D,
           cx + ux * r * 0.35, cy + uy * r * 0.35,
           cx + px * r * 0.78 + ux * r, cy + py * r * 0.78 + uy * r, tipx, tipy,
           cx - px * r * 0.78 + ux * r, cy - py * r * 0.78 + uy * r,
           cx + ux * r * 0.35, cy + uy * r * 0.35, col,
           cx + ux * r * 0.5, cy + uy * r * 0.5,
           cx + px * r * 0.25 + ux * r, cy + py * r * 0.25 + uy * r, tipx, tipy,
           CREAM, max(0.7, r * 0.16)))


# ================================================================ 1. TORAN
def make_toran(w=1400, h=340, strands=30, seed=5):
    rng = random.Random(seed)
    out = []
    sag = h * 0.13

    def rope_y(t):
        return 12 + sag * math.sin(math.pi * t) ** 0.85

    # leaf swags behind the rope
    for i in range(strands + 1):
        t = i / strands
        x, y = t * w, rope_y(t)
        out.append(leaf(x, y + 3, 40, 116 + rng.uniform(-14, 14), LEAF, LEAF_D))
        out.append(leaf(x, y + 3, 36, 64 + rng.uniform(-14, 14), LEAF_L, LEAF_D))

    pts = " ".join("%.1f,%.1f" % (k / 140 * w, rope_y(k / 140)) for k in range(141))
    out.append('<polyline points="%s" stroke="%s" stroke-width="4" fill="none"/>' % (pts, LEAF_D))

    # hanging strands — lengths follow two beating waves so the rhythm reads
    # as designed rather than random
    for i in range(strands + 1):
        t = i / strands
        x, y = t * w, rope_y(t)
        wave = 0.5 + 0.5 * math.sin(i * 0.9) * math.cos(i * 0.31)
        n_beads = int(3 + wave * 9)
        gap = 21
        tip = y + 18 + n_beads * gap
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.7" opacity=".7"/>'
                   % (x, y, x, tip, LEAF_D))
        for b in range(n_beads):
            by = y + 18 + b * gap
            if b % 4 == 3:
                out.append('<circle cx="%.1f" cy="%.1f" r="5.5" fill="%s"/>' % (x, by, CREAM))
                out.append('<circle cx="%.1f" cy="%.1f" r="2.6" fill="%s" opacity=".55"/>' % (x, by, SHELL))
            else:
                out.append(use_mari(x, by, 10.5 if b % 3 else 8.0))
        out.append('<path d="M%.1f %.1f q5 7 0 13 q-5-6 0-13z" fill="%s"/>' % (x, tip, GOLD))

    return svg(w, h, "".join(out), defs=marigold_def())


# ================================================================ 2. ARCH
def arch_points(w, h, spring, n=400):
    """Left jamb up, then over the superelliptic head, then right jamb down."""
    pts = []
    for i in range(n + 1):
        t = i / n
        if t < 0.34:
            pts.append((0.0, h - (t / 0.34) * (h - spring)))
        elif t < 0.66:
            u = (t - 0.34) / 0.32
            ang = u * math.pi
            x = w / 2 - math.cos(ang) * (w / 2)
            k = abs(math.cos(ang))
            y = spring - spring * (1 - k ** 2.6) ** (1 / 2.2)
            pts.append((x, y))
        else:
            pts.append((w, spring + ((t - 0.66) / 0.34) * (h - spring)))
    return pts


def resample(pts, n):
    """Even spacing by arc length — keeps every cusp the same size."""
    d = [0.0]
    for i in range(1, len(pts)):
        d.append(d[-1] + math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]))
    total, out, j = d[-1], [], 0
    for i in range(n + 1):
        target = total * i / n
        while j < len(d) - 2 and d[j + 1] < target:
            j += 1
        span = d[j + 1] - d[j]
        k = 0 if span == 0 else (target - d[j]) / span
        out.append((pts[j][0] + (pts[j + 1][0] - pts[j][0]) * k,
                    pts[j][1] + (pts[j + 1][1] - pts[j][1]) * k))
    return out


def make_arch(w=820, h=1040, cusps=26, band=34):
    out = []
    spring = h * 0.50

    outer = arch_points(w, h, spring)
    inner = [(x + band if x < w / 2 else x - band,
              y + band * 0.86 if y > spring else y + band * 0.92) for (x, y) in
             arch_points(w - 2 * band, h, spring - band * 0.9)]
    inner = [(x + band, y) for (x, y) in arch_points(w - 2 * band, h, spring - band * 0.9)]

    def dpath(pts, close=True):
        d = "M%.1f %.1f " % pts[0] + " ".join("L%.1f %.1f" % p for p in pts[1:])
        return d + " Z" if close else d

    # the gold band, as an even-odd ring, filled with a foil gradient
    out.append('<path d="%s %s" fill="url(#foil)" fill-rule="evenodd"/>'
               % (dpath(outer + [(w, h), (0, h)]), dpath(inner + [(w - band, h), (band, h)])))
    out.append('<path d="%s" stroke="%s" stroke-width="2.4" fill="none"/>' % (dpath(outer, False), GOLD_D))
    out.append('<path d="%s" stroke="%s" stroke-width="1.8" fill="none"/>' % (dpath(inner, False), GOLD_D))

    # cusped inner edge — only across the head
    head = [p for p in inner if p[1] <= spring - band * 0.9 + 1]
    picks = resample(head, cusps)
    d = "M%.1f %.1f " % picks[0]
    for i in range(1, len(picks)):
        x0, y0 = picks[i - 1]
        x1, y1 = picks[i]
        r = math.hypot(x1 - x0, y1 - y0) / 2 * 1.02
        d += "A%.1f %.1f 0 0 0 %.1f %.1f " % (r, r, x1, y1)
    out.append('<path d="%s" stroke="%s" stroke-width="3.4" fill="none" stroke-linecap="round"/>' % (d, GOLD_D))
    out.append('<path d="%s" stroke="%s" stroke-width="1.4" fill="none" opacity=".9"/>' % (d, GOLD_P))
    for (x, y) in picks:
        out.append('<circle cx="%.1f" cy="%.1f" r="3.4" fill="%s"/>' % (x, y, GOLD_P))

    # beading along the outer edge
    for p in resample(outer, 90):
        out.append('<circle cx="%.1f" cy="%.1f" r="2.1" fill="%s" opacity=".8"/>' % (p[0], p[1], GOLD_P))

    # jamb filigree
    for bx in (band / 2, w - band / 2):
        y = spring + 34
        while y < h - 30:
            out.append('<circle cx="%.1f" cy="%.1f" r="5.5" stroke="%s" stroke-width="1.4" fill="none"/>' % (bx, y, GOLD_P))
            out.append('<circle cx="%.1f" cy="%.1f" r="2" fill="%s"/>' % (bx, y, GOLD_D))
            y += 46

    # lotus-bud finial
    out.append('<path d="M%g %g q15 18 0 38 q-15-20 0-38z" fill="%s"/>' % (w / 2, -6, GOLD))
    out.append('<circle cx="%g" cy="%g" r="6" fill="%s"/>' % (w / 2, 42, GOLD_D))

    foil = ('<linearGradient id="foil" x1="0" y1="0" x2="1" y2="0.35">'
            '<stop offset="0" stop-color="%s"/><stop offset=".18" stop-color="%s"/>'
            '<stop offset=".38" stop-color="%s"/><stop offset=".56" stop-color="%s"/>'
            '<stop offset=".78" stop-color="%s"/><stop offset="1" stop-color="%s"/>'
            '</linearGradient>' % (GOLD_D, GOLD, GOLD_P, GOLD_L, GOLD, GOLD_D))
    return svg(w, h, "".join(out), defs=foil)


# ================================================================ 3. MANDALA
def make_mandala(size=520):
    c = size / 2
    out = []

    def ring_petals(r_in, r_out, n, col, sw, phase=0.0):
        seg = []
        for i in range(n):
            a = 2 * math.pi * i / n + phase
            x0, y0 = c + math.cos(a) * r_in, c + math.sin(a) * r_in
            x1, y1 = c + math.cos(a) * r_out, c + math.sin(a) * r_out
            wa = math.pi / n * 0.85
            m = (r_in + r_out) / 2
            seg.append("M%.1f %.1f Q%.1f %.1f %.1f %.1f Q%.1f %.1f %.1f %.1f"
                       % (x0, y0, c + math.cos(a - wa) * m, c + math.sin(a - wa) * m, x1, y1,
                          c + math.cos(a + wa) * m, c + math.sin(a + wa) * m, x0, y0))
        out.append('<path d="%s" stroke="%s" stroke-width="%.1f" fill="none"/>' % (" ".join(seg), col, sw))

    for r in (0.97, 0.93, 0.66, 0.62, 0.34, 0.30):
        out.append('<circle cx="%g" cy="%g" r="%.1f" stroke="%s" stroke-width="1.2" fill="none"/>' % (c, c, c * r, GOLD))
    ring_petals(c * 0.66, c * 0.93, 32, GOLD, 1.1)
    ring_petals(c * 0.34, c * 0.62, 24, GOLD, 1.3, math.pi / 24)
    ring_petals(c * 0.10, c * 0.30, 16, GOLD, 1.4)
    for i in range(48):
        a = 2 * math.pi * i / 48
        out.append('<circle cx="%.1f" cy="%.1f" r="2" fill="%s"/>'
                   % (c + math.cos(a) * c * 0.795, c + math.sin(a) * c * 0.795, GOLD))
    out.append('<circle cx="%g" cy="%g" r="%.1f" fill="%s"/>' % (c, c, c * 0.07, GOLD))
    return svg(size, size, "".join(out))


# ================================================================ 4. CORNER
def make_corner(w=560, h=560, seed=9, flip=False):
    """A dense spray anchored in the bottom corner, thinning as it reaches out."""
    rng = random.Random(seed)
    out = []
    ox, oy = 40.0, h - 30.0              # anchor
    A0, A1 = math.radians(-96), math.radians(6)
    R = h * 0.92

    def place(frac_r, frac_a, jitter=0.0):
        a = A0 + (A1 - A0) * frac_a + rng.uniform(-jitter, jitter)
        r = R * frac_r
        return ox + math.cos(a) * r, oy + math.sin(a) * r

    # --- foliage, two layers -------------------------------------------
    for i in range(40):
        fr, fa = rng.uniform(0.10, 1.0), rng.uniform(0, 1)
        x, y = place(fr, fa, 0.10)
        ln = (105 - 55 * fr) * rng.uniform(0.75, 1.2)
        ang = math.degrees(math.atan2(y - oy, x - ox)) + rng.uniform(-55, 55)
        out.append(leaf(x, y, ln, ang, [LEAF_D, LEAF, LEAF_L][i % 3], LEAF_D))

    # --- roses: big near the corner, small at the tips -------------------
    roses = [(0.13, 0.30, 54), (0.28, 0.62, 43), (0.30, 0.16, 36), (0.46, 0.42, 33),
             (0.50, 0.80, 28), (0.62, 0.22, 25), (0.70, 0.58, 22), (0.84, 0.38, 17)]
    for k, (fr, fa, rr) in enumerate(roses):
        x, y = place(fr, fa)
        out.append(rose(x, y, rr, seed + k))

    # --- marigolds for warmth -------------------------------------------
    for k in range(7):
        x, y = place(rng.uniform(0.18, 0.86), rng.uniform(0, 1), 0.06)
        out.append(use_mari(x, y, rng.uniform(11, 19)))

    # --- jasmine + buds fill the gaps ------------------------------------
    for k in range(22):
        x, y = place(rng.uniform(0.12, 1.0), rng.uniform(0, 1), 0.10)
        out.append(jasmine(x, y, rng.uniform(9, 16)))
    for k in range(10):
        x, y = place(rng.uniform(0.45, 1.0), rng.uniform(0, 1), 0.10)
        out.append(bud(x, y, rng.uniform(7, 12),
                       math.degrees(math.atan2(y - oy, x - ox)),
                       [ROSE, ROSE_L, MARI_L][k % 3]))

    body = "".join(out)
    if flip:
        body = '<g transform="translate(%g 0) scale(-1 1)">%s</g>' % (w, body)
    return svg(w, h, body, defs=marigold_def())


# ================================================================ 5. PEACOCK
def make_peacock(w=520, h=620):
    """Stylised peacock — barbed plumes, not bare wires."""
    out = []
    bx, by = w * 0.50, h * 0.82

    def plume(a, L, col, eye=True, blade=True, op=".85"):
        """Stem + a soft tapering blade, so the tail reads as plumage."""
        p = []
        ex, ey = bx + math.cos(a) * L, by + math.sin(a) * L
        mx, my = bx + math.cos(a + 0.12) * L * 0.55, by + math.sin(a + 0.12) * L * 0.55
        if blade:
            wx, wy = -math.sin(a) * L * 0.062, math.cos(a) * L * 0.062
            p.append('<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f Q%.1f %.1f %.1f %.1f Z" '
                     'fill="%s" opacity="%s"/>'
                     % (bx, by, mx + wx, my + wy, ex, ey, mx - wx, my - wy, bx, by, col, op))
        p.append('<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f" stroke="%s" stroke-width="1.6" '
                 'fill="none" opacity=".9"/>' % (bx, by, mx, my, ex, ey, col))
        if eye:
            for (rx, ry, c) in ((15, 19, TEAL_L), (11, 14, TEAL_D), (7.5, 9.5, BLUE_D), (4, 5, GOLD)):
                p.append('<ellipse cx="%.1f" cy="%.1f" rx="%g" ry="%g" fill="%s" %s/>'
                         % (ex, ey, rx, ry, c, rot(a, ex, ey)))
        return "".join(p)

    # a soft under-layer, then the eyed plumes over it
    for i in range(30):
        t = i / 29.0
        out.append(plume(math.radians(-172 + t * 164), h * (0.50 + 0.10 * math.sin(t * math.pi)),
                         TEAL_D, eye=False, op=".28"))
    for i in range(19):
        t = i / 18.0
        out.append(plume(math.radians(-158 + t * 136), h * (0.62 + 0.14 * math.sin(t * math.pi)),
                         [TEAL, TEAL_L, TEAL_D][i % 3], op=".45"))

    # body and neck
    hx, hy = bx + 14, by - 136
    out.append('<path d="M%.1f %.1f q34 -20 38 -62 q4 -48 -18 -76" stroke="%s" stroke-width="19" '
               'fill="none" stroke-linecap="round"/>' % (bx - 2, by, TEAL_D))
    out.append('<ellipse cx="%.1f" cy="%.1f" rx="32" ry="41" fill="%s"/>' % (bx - 4, by + 8, TEAL_D))
    out.append('<ellipse cx="%.1f" cy="%.1f" rx="24" ry="31" fill="%s"/>' % (bx - 8, by + 5, TEAL))

    out.append('<circle cx="%.1f" cy="%.1f" r="15" fill="%s"/>' % (hx, hy, TEAL_D))
    out.append('<path d="M%.1f %.1f l20 7 l-20 7z" fill="%s"/>' % (hx + 11, hy - 5, GOLD))
    out.append('<circle cx="%.1f" cy="%.1f" r="3.2" fill="%s"/>' % (hx + 5, hy - 5, CREAM))
    for k in range(3):
        a = math.radians(-98 + k * 17)
        ex, ey = hx + math.cos(a) * 24, hy - 13 + math.sin(a) * 24
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2"/>'
                   % (hx, hy - 13, ex, ey, TEAL_D))
        out.append('<circle cx="%.1f" cy="%.1f" r="3.6" fill="%s"/>' % (ex, ey, GOLD))
    return svg(w, h, "".join(out))


# ================================================================ 6. KALASHA
def make_kalasha(w=280, h=360):
    out = []
    cx = w / 2
    for ang, ln in [(-142, 104), (-118, 116), (-90, 124), (-62, 116), (-38, 104)]:
        out.append(leaf(cx, h * 0.46, ln, ang, LEAF, LEAF_D))
    pot = "M%g %g q-62 32 -62 82 q0 66 62 66 q62 0 62 -66 q0 -50 -62 -82z" % (cx, h * 0.44)
    out.append('<path d="%s" fill="%s"/>' % (pot, GOLD))
    out.append('<path d="%s" stroke="%s" stroke-width="2.6" fill="none"/>' % (pot, GOLD_D))
    out.append('<rect x="%g" y="%g" width="84" height="15" rx="6" fill="%s"/>' % (cx - 42, h * 0.40, GOLD_D))
    out.append('<rect x="%g" y="%g" width="100" height="10" rx="5" fill="%s"/>' % (cx - 50, h * 0.365, GOLD))
    out.append('<ellipse cx="%g" cy="%g" rx="29" ry="34" fill="#8B5E3C"/>' % (cx, h * 0.285))
    out.append('<ellipse cx="%g" cy="%g" rx="29" ry="34" stroke="%s" stroke-width="2" fill="none"/>' % (cx, h * 0.285, GOLD_D))
    for yy in (0.63, 0.73):
        out.append('<path d="M%g %g q52 16 104 0" stroke="%s" stroke-width="2.6" fill="none" opacity=".8"/>'
                   % (cx - 52, h * yy, GOLD_P))
    return svg(w, h, "".join(out))


# ================================================================ 7. DIVIDER
def make_divider(w=680, h=90):
    out = []
    cy = h / 2
    for s in (-1, 1):
        x0, x1 = w / 2 + s * 46, w / 2 + s * (w / 2 - 10)
        out.append('<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f" stroke="%s" stroke-width="1.8" fill="none"/>'
                   % (x0, cy, (x0 + x1) / 2, cy - 13, x1, cy, GOLD))
        out.append('<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f" stroke="%s" stroke-width="1.1" fill="none" opacity=".75"/>'
                   % (x0, cy, (x0 + x1) / 2, cy + 13, x1, cy, GOLD_D))
        for k in (0.34, 0.60, 0.84):
            out.append('<circle cx="%.1f" cy="%.1f" r="3" fill="%s"/>' % (x0 + (x1 - x0) * k, cy - 6 + k * 4, GOLD))
        out.append('<path d="M%.1f %.1f q%g -11 %g 0 q%g 11 %g 0z" fill="%s"/>'
                   % (x1 - s * 16, cy, s * 8, s * 16, s * -8, s * -16, GOLD_L))
    cx = w / 2
    out.append(petal_ring(cx, cy, 20, 7, GOLD, 0.62, 0.34, 0.95, math.pi))
    out.append('<circle cx="%.1f" cy="%.1f" r="6" fill="%s"/>' % (cx, cy, GOLD_D))
    return svg(w, h, "".join(out))


# ================================================================ SCENE PARTS
#
# The event cards are 9:16 portraits: sky wash and text on top, a ground scene
# across the bottom. Each scene below is drawn at 600x480 and sits at the foot
# of its card.

BRASS_D, BRASS, BRASS_L = "#8A5A12", "#B8860B", "#D9A93A"
STONE_D, STONE, STONE_L = "#7E6647", "#9C8261", "#BCA382"
WOOD_D,  WOOD,  WOOD_L  = "#6B4423", "#8B5E3C", "#A87A50"


def ground(w, y, h, col_far, col_near, seed=1):
    """A softly undulating band of ground."""
    n = 26
    d = "M0 %.1f " % y
    for i in range(1, n + 1):
        d += "L%.1f %.1f " % (w * i / n, y + math.sin(i * 0.8 + seed) * 3.5)
    d += "L%g %g L0 %g Z" % (w, y + h, y + h)
    near = "M0 %.1f " % (y + h * 0.42)
    for i in range(1, n + 1):
        near += "L%.1f %.1f " % (w * i / n, y + h * 0.42 + math.cos(i * 0.7 + seed) * 4)
    near += "L%g %g L0 %g Z" % (w, y + h, y + h)
    return ('<path d="%s" fill="%s"/><path d="%s" fill="%s"/>'
            % (d, col_far, near, col_near))


def banana(x, base_y, size, flip=False):
    """A banana / traveller's-palm clump — the coastal Karnataka staple."""
    out = []
    spec = [(-152, .72), (-124, .95), (-98, 1.08), (-72, .95), (-44, .74), (-18, .55)]
    for k, (ang, f) in enumerate(spec):
        a = 180 - ang if flip else ang
        out.append(leaf(x, base_y, size * f, a, [LEAF_D, LEAF, LEAF_L][k % 3], LEAF_D))
    out.append('<path d="M%.1f %.1f l-3 %.1f h6 z" fill="%s"/>'
               % (x, base_y - size * .1, size * .12, LEAF_D))
    return "".join(out)


def pot(cx, base_y, w, h, col=BRASS, rim=BRASS_D):
    """A brass pot — round belly narrowing to a necked rim."""
    d = ("M%.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f Z"
         % (cx - w * .30, base_y - h * .86,
            cx - w * .58, base_y - h * .60, cx - w * .52, base_y - h * .05, cx, base_y,
            cx + w * .52, base_y - h * .05, cx + w * .58, base_y - h * .60, cx + w * .30, base_y - h * .86))
    return ('<path d="%s" fill="%s"/>'
            '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" fill="%s"/>'
            '<path d="M%.1f %.1f q%.1f %.1f %.1f 0" stroke="%s" stroke-width="%.1f" fill="none" opacity=".5"/>'
            % (d, col,
               cx - w * .40, base_y - h, w * .80, h * .15, h * .05, rim,
               cx - w * .32, base_y - h * .46, w * .32, h * .14, w * .64, BRASS_L, max(1.0, h * .05)))


def kalasha_at(cx, base_y, s):
    """Pot + coconut + mango leaves, scaled to `s` (1.0 ≈ 90px tall)."""
    out = [pot(cx, base_y, 46 * s, 52 * s, GOLD, GOLD_D)]
    for ang, ln in [(-140, 26), (-112, 30), (-90, 33), (-68, 30), (-40, 26)]:
        out.append(leaf(cx, base_y - 52 * s, ln * s, ang, LEAF, LEAF_D))
    out.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="#8B5E3C"/>'
               % (cx, base_y - 64 * s, 11 * s, 13 * s))
    return "".join(out)


def pillar(cx, top, bottom, w, col=GOLD, dark=GOLD_D):
    """A mandap pillar: base, shaft, capital."""
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>'
            '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="%s"/>'
            '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="%s"/>'
            '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity=".35"/>'
            % (cx - w / 2, top, w, bottom - top, col,
               cx - w * .85, top, w * 1.7, w * .38, dark,
               cx - w * .85, bottom - w * .34, w * 1.7, w * .34, dark,
               cx - w * .34, top, w * .26, bottom - top, GOLD_P))


def gopuram_at(cx, base_y, w, h, tiers=6):
    """A stepped temple tower silhouette."""
    out = []
    for i in range(tiers):
        t = i / tiers
        tw = w * (1 - .60 * t)
        th = h / tiers
        y = base_y - (i + 1) * th
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>'
                   % (cx - tw / 2, y, tw, th, GOLD if i % 2 else GOLD_D))
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity=".8"/>'
                   % (cx - tw / 2 - 3, y, tw + 6, th * .18, GOLD_L))
        if i < 3:
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" fill="%s"/>'
                       % (cx - tw * .09, y + th * .30, tw * .18, th * .55, tw * .05, "#7C1F1A"))
    # crowning finials
    ty = base_y - h
    for dx in (-w * .18, 0, w * .18):
        out.append('<path d="M%.1f %.1f q4 -9 0 -14 q-4 5 0 14z" fill="%s"/>' % (cx + dx, ty, GOLD_L))
    return "".join(out)


def curtain(x0, x1, top_y, length, step=19, r=6.2, phase=0.0):
    """Marigold strands hanging as a backdrop curtain."""
    out = []
    x, i = x0, 0
    while x <= x1:
        L = length * (.78 + .22 * math.sin(i * .8 + phase))
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.2" opacity=".5"/>'
                   % (x, top_y, x, top_y + L, LEAF_D))
        n = int(L / (r * 2.05))
        for b in range(n):
            out.append(use_mari(x, top_y + r + b * r * 2.05, r if b % 3 else r * .78))
        x += step
        i += 1
    return "".join(out)


def diya(cx, base_y, s=1.0):
    """A small clay lamp. The halo is drawn first so it reads as light
    spilling out, not as a disc sitting on top of the flame."""
    return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" opacity=".16"/>'
            '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" opacity=".22"/>'
            '<path d="M%.1f %.1f q%.1f %.1f %.1f 0 z" fill="%s"/>'
            '<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s"/>'
            '<path d="M%.1f %.1f q%.1f %.1f 0 %.1f q%.1f %.1f 0 %.1f z" fill="%s"/>'
            % (cx, base_y - 13 * s, 21 * s, MARI_P,
               cx, base_y - 13 * s, 12 * s, "#FFF0BE",
               cx - 11 * s, base_y - 6 * s, 11 * s, 11 * s, 22 * s, BRASS,
               cx, base_y - 6 * s, 11 * s, 3.4 * s, BRASS_L,
               cx, base_y - 8 * s, 5 * s, -7 * s, -13 * s, -5 * s, 6 * s, 13 * s, "#FFE08A"))


def lamp_stand(cx, base_y, h, s=1.0):
    """A deepa stambha — the tiered brass lamp column."""
    out = ['<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>'
           % (cx - 4 * s, base_y - h, 8 * s, h, BRASS)]
    out.append('<path d="M%.1f %.1f h%.1f l%.1f %.1f h%.1f z" fill="%s"/>'
               % (cx - 20 * s, base_y, 40 * s, -7 * s, -10 * s, -26 * s, BRASS_D))
    for k, fy in enumerate((.34, .58, .80)):
        y = base_y - h * fy
        wdt = (22 - k * 4) * s
        out.append('<path d="M%.1f %.1f q%.1f %.1f %.1f 0 z" fill="%s"/>'
                   % (cx - wdt, y, wdt, 9 * s, wdt * 2, BRASS_L))
        out.append(diya(cx - wdt * .62, y, s * .5))
        out.append(diya(cx + wdt * .62, y, s * .5))
    out.append(diya(cx, base_y - h, s * .72))
    return "".join(out)


def lantern(cx, top_y, drop, s=1.0, col=MARI):
    """A hanging lantern: chain, brass cap, and a glowing glass globe."""
    b = top_y + drop
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.4" opacity=".7"/>'
            '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" opacity=".18"/>'
            '<path d="M%.1f %.1f h%.1f l%.1f %.1f h%.1f z" fill="%s"/>'
            '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" opacity=".9"/>'
            '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>'
            '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" opacity=".55"/>'
            '<path d="M%.1f %.1f q%.1f %.1f 0 %.1f z" fill="%s"/>'
            % (cx, top_y, cx, b, GOLD_D,
               cx, b + 15 * s, 30 * s, MARI_P,
               cx - 11 * s, b, 22 * s, -4 * s, -7 * s, -14 * s, GOLD_D,
               cx, b + 15 * s, 15 * s, col,
               cx, b + 15 * s, 11 * s, "#FFE49C",
               cx - 4 * s, b + 11 * s, 4 * s, CREAM,
               cx - 7 * s, b + 30 * s, 7 * s, 9 * s, 14 * s, GOLD_D))


def lotus(cx, cy, r):
    """A lotus bloom — three rings of narrowing petals around a gold heart."""
    return (petal_ring(cx, cy, r, 8, ROSE, .58, .24, 1.00, 0.0)
            + petal_ring(cx, cy, r * .76, 7, ROSE_L, .55, .26, 1.00, .42)
            + petal_ring(cx, cy, r * .48, 5, ROSE_P, .50, .30, 1.00, .84)
            + '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (cx, cy, r * .17, MARI_P))


def swag(x0, x1, y, sag, r=5.5, step=17):
    """A garland slung between two points."""
    out = []
    n = int((x1 - x0) / step)
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append((x0 + (x1 - x0) * t, y + sag * math.sin(math.pi * t) ** .9))
    out.append('<polyline points="%s" stroke="%s" stroke-width="2" fill="none"/>'
               % (" ".join("%.1f,%.1f" % p for p in pts), LEAF_D))
    for i, (px, py) in enumerate(pts):
        out.append(use_mari(px, py, r if i % 3 else r * .8))
    return "".join(out)


# ================================================================ 8. GARLAND STRAND
def make_garland_side(w=120, h=760, seed=3):
    """A long hanging strand for the edges of an event card:
    mallige, rudraksha beads and a brass temple bell."""
    rng = random.Random(seed)
    out = []
    cx = w / 2

    out.append('<line x1="%g" y1="0" x2="%g" y2="%g" stroke="%s" stroke-width="2" opacity=".55"/>'
               % (cx, cx, h * .86, LEAF_D))

    y = 16
    i = 0
    while y < h * .84:
        if i % 4 == 3:
            out.append('<circle cx="%.1f" cy="%.1f" r="7" fill="%s"/>' % (cx, y, "#6E2A18"))
            out.append('<circle cx="%.1f" cy="%.1f" r="3" fill="%s" opacity=".5"/>' % (cx, y, "#3F1408"))
        elif i % 4 == 1:
            out.append(jasmine(cx, y, 9.5))
        else:
            out.append(use_mari(cx, y, 9 if i % 2 else 7))
        y += 20
        i += 1

    # brass bell at the tip
    by = h * .86
    out.append('<path d="M%.1f %.1f q0 -16 14 -16 q14 0 14 16 q3 6 5 10 h-38 q2 -4 5 -10z" fill="%s" transform="translate(%.1f 0)"/>'
               % (0, by, BRASS, cx - 14))
    out.append('<rect x="%.1f" y="%.1f" width="34" height="5" rx="2.5" fill="%s"/>' % (cx - 17, by + 10, BRASS_D))
    out.append('<path d="M%.1f %.1f q3 9 0 13 q-3-4 0-13z" fill="%s"/>' % (cx, by + 15, BRASS_L))
    out.append('<circle cx="%.1f" cy="%.1f" r="4" stroke="%s" stroke-width="2" fill="none"/>'
               % (cx, by - 19, BRASS_D))
    return svg(w, h, "".join(out), defs=marigold_def())


# ================================================================ 9. SCENES
#
# Composed to fill 600x420 edge to edge — the card places each scene along its
# bottom, so empty space at the top of the box would just read as a gap.
SW, SH = 600, 420


def make_scene_dhare():
    """The wedding mandap: gopuram behind, pillared canopy, marigold curtain."""
    out = []
    out.append(gopuram_at(300, 196, 205, 150))

    # canopy
    out.append('<path d="M56 166 L116 134 H484 L544 166 Z" fill="%s"/>' % GOLD_D)
    out.append('<rect x="68" y="162" width="464" height="22" rx="4" fill="%s"/>' % GOLD)
    out.append('<rect x="68" y="162" width="464" height="6" fill="%s" opacity=".8"/>' % GOLD_P)

    out.append(curtain(140, 462, 186, 112, step=18, r=5.6))

    out.append(pillar(105, 174, 352, 26))
    out.append(pillar(495, 174, 352, 26))

    out.append(ground(SW, 338, 82, LEAF_D, "#24422A", seed=2))

    out.append(kalasha_at(152, 350, .9))
    out.append(kalasha_at(448, 350, .9))
    out.append(banana(32, 368, 96))
    out.append(banana(568, 368, 96, flip=True))
    for x in (252, 300, 348):
        out.append(diya(x, 376, .8))
    return svg(SW, SH, "".join(out), defs=marigold_def())


def make_scene_haldi():
    """Mangala Snana: a marigold backdrop, the low seat, turmeric pots."""
    out = []
    # the backdrop wall of marigold strands behind the seat
    out.append('<rect x="104" y="34" width="392" height="10" rx="5" fill="%s"/>' % LEAF_D)
    out.append(curtain(116, 484, 44, 250, step=21, r=5.6, phase=.6))

    out.append(ground(SW, 334, 86, LEAF, "#35603A", seed=5))

    # the low wooden seat
    out.append('<path d="M238 290 q62 -28 124 0z" fill="%s" opacity=".4"/>' % MARI_P)
    out.append('<rect x="232" y="290" width="136" height="16" rx="4" fill="%s"/>' % WOOD)
    out.append('<rect x="232" y="290" width="136" height="5" fill="%s" opacity=".7"/>' % WOOD_L)
    for lx in (244, 348):
        out.append('<rect x="%d" y="306" width="10" height="42" fill="%s"/>' % (lx, WOOD_D))

    # brass pots either side
    for x in (78, 122, 166):
        out.append(pot(x, 348, 40, 46))
    for x in (434, 478, 522):
        out.append(pot(x, 348, 40, 46))

    # turmeric plates in front
    for x, s in ((262, 1.0), (300, 1.15), (338, 1.0)):
        out.append('<ellipse cx="%d" cy="360" rx="%.1f" ry="%.1f" fill="%s"/>' % (x, 20 * s, 7 * s, BRASS_L))
        out.append('<ellipse cx="%d" cy="357" rx="%.1f" ry="%.1f" fill="%s"/>' % (x, 15 * s, 5 * s, "#E8A72C"))

    out.append(banana(30, 366, 92))
    out.append(banana(570, 366, 92, flip=True))
    return svg(SW, SH, "".join(out), defs=marigold_def())


def make_scene_mehendi():
    """Mehendi: hanging lanterns, a low divan, a tray of henna cones."""
    out = []
    out.append(swag(30, 570, 14, 38, r=5.0))
    for cx, drop, s in ((84, 128, 1.0), (172, 182, .82), (428, 166, .85), (516, 116, 1.05)):
        out.append(lantern(cx, 22, drop, s, MARI_L))

    # a low patterned screen behind the seating
    out.append('<rect x="150" y="212" width="300" height="112" rx="8" fill="%s" opacity=".22"/>' % LEAF_D)
    for i in range(9):
        x = 168 + i * 35
        out.append('<path d="M%d 318 C%d 296 %d 276 %d 250 C%d 262 %d 292 %d 318z" fill="%s" opacity=".35"/>'
                   % (x, x - 11, x - 13, x, x + 13, x + 11, x, CREAM))
    out.append('<rect x="150" y="206" width="300" height="9" rx="4" fill="%s"/>' % WOOD_D)

    out.append(ground(SW, 336, 84, "#35603A", "#24422A", seed=8))

    # divan with cushions
    for cxp, col in ((222, ROSE), (266, ROSE_L), (334, ROSE), (378, ROSE_L)):
        out.append('<rect x="%.1f" y="256" width="42" height="30" rx="10" fill="%s"/>' % (cxp - 21, col))
    out.append('<rect x="180" y="286" width="240" height="24" rx="7" fill="%s"/>' % WOOD)
    out.append('<rect x="180" y="286" width="240" height="6" fill="%s" opacity=".7"/>' % WOOD_L)
    out.append('<rect x="180" y="310" width="240" height="12" rx="5" fill="%s"/>' % WOOD_D)
    for lx in (194, 396):
        out.append('<rect x="%d" y="322" width="14" height="26" fill="%s"/>' % (lx, WOOD_D))

    # a brass tray of henna cones on the floor
    out.append('<ellipse cx="300" cy="360" rx="34" ry="11" fill="%s"/>' % BRASS)
    out.append('<ellipse cx="300" cy="357" rx="27" ry="8" fill="%s"/>' % BRASS_L)
    for dx, ang in ((-13, -108), (0, -92), (13, -74)):
        out.append('<path d="M%d 354 q5 -20 0 -26 q-5 6 0 26z" fill="%s" transform="rotate(%d 300 354)"/>'
                   % (300 + dx, LEAF_D, ang + 90))

    out.append(banana(24, 366, 104))
    out.append(banana(576, 366, 104, flip=True))
    out.append(banana(86, 372, 68))
    out.append(banana(514, 372, 68, flip=True))
    for x in (132, 176, 424, 468):
        out.append(diya(x, 374, .8))
    return svg(SW, SH, "".join(out), defs=marigold_def())


def make_scene_lamp():
    """Aratakshate: an evening of brass lamp stands and a lotus pond."""
    out = []
    out.append(swag(16, 584, 12, 44, r=5.4))
    out.append(ground(SW, 300, 120, "#1E4438", "#14302A", seed=11))

    out.append(lamp_stand(84, 348, 232, 1.35))
    out.append(lamp_stand(516, 348, 232, 1.35))
    out.append(lamp_stand(172, 344, 168, .95))
    out.append(lamp_stand(428, 344, 168, .95))

    # garlanded swags strung between the stands
    out.append(swag(104, 496, 196, 26, r=4.6, step=15))
    out.append(swag(190, 410, 252, 20, r=4.0, step=13))

    # two rows of diyas along the front
    for i in range(13):
        out.append(diya(28 + i * 45, 358, .85))
    for i in range(12):
        out.append(diya(50 + i * 45, 376, .7))

    # lotus pond
    out.append('<path d="M0 384 h600 v36 H0 z" fill="%s" opacity=".5"/>' % TEAL_D)
    for x in (56, 168, 300, 432, 548):
        out.append('<ellipse cx="%d" cy="406" rx="28" ry="9" fill="%s" opacity=".55"/>' % (x, LEAF_D))
    for cxp, sc in ((110, 1.0), (232, .85), (300, 1.3), (378, .85), (492, 1.0)):
        out.append(lotus(cxp, 396, 17 * sc))
    return svg(SW, SH, "".join(out), defs=marigold_def())


# ================================================================ write all
print("drawing ornament...")
save("toran.svg",        make_toran())
save("arch.svg",         make_arch())
save("mandala.svg",      make_mandala())
save("corner-left.svg",  make_corner(seed=9))
save("corner-right.svg", make_corner(seed=17, flip=True))
save("peacock.svg",      make_peacock())
save("kalasha.svg",      make_kalasha())
save("divider.svg",      make_divider())

# event-card artwork. The four ground scenes are no longer drawn here —
# they are painted rasters now, see tools/generate_scenes.py.
save("garland-side.svg",  make_garland_side())
print("done.")
