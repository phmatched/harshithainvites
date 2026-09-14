"""Paint the four event-card scenes.

Each is an RGBA painting whose top fades to transparent, so it composites onto
the sky of the card it sits on. Painted far-to-near: haze-softened distance
first, architecture next, foreground foliage last.

    python3 tools/generate_scenes.py
"""

import math, random, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paint import Painting, mix, shade                       # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "assets", "img") + os.sep

W, H = 640, 440

# ---------------------------------------------------------------- palette
LEAF_FAR   = (88, 122, 78)
LEAF_MID   = (60, 98, 60)
LEAF_NEAR  = (38, 70, 44)
LEAF_LIT   = (122, 154, 84)

GRASS_FAR  = (108, 136, 84)
GRASS_NEAR = (52, 84, 56)

MARI_D, MARI, MARI_L = (176, 92, 12), (224, 130, 20), (246, 176, 58)
BRASS_D, BRASS, BRASS_L = (120, 80, 20), (176, 128, 38), (224, 186, 96)
GOLD_D, GOLD, GOLD_L = (140, 102, 26), (198, 154, 44), (238, 208, 130)
STONE      = (176, 148, 104)
WOOD       = (122, 82, 48)
ROSE       = (198, 116, 130)
FLAME      = (255, 214, 132)
CREAMY     = (252, 246, 230)


# ---------------------------------------------------------------- shapes
def sym_poly(cx, base_y, w, h, profile):
    """Mirror a half-profile of (x_frac, y_frac_from_base) into a closed shape."""
    right = [(cx + w * fx, base_y - h * fy) for fx, fy in profile]
    left = [(cx - w * fx, base_y - h * fy) for fx, fy in reversed(profile)]
    return right + left


POT_PROFILE = [(0.00, 0.00), (0.30, 0.03), (0.48, 0.18), (0.54, 0.42),
               (0.46, 0.68), (0.30, 0.84), (0.32, 0.94), (0.30, 1.00), (0.00, 1.00)]


def pot(p, cx, base_y, w, h, col=BRASS, seed=1):
    p.shadow(cx, base_y + h * 0.05, w * 0.95, h * 0.16, 0.42)
    p.poly(sym_poly(cx, base_y, w, h, POT_PROFILE), col,
           light=(-0.78, -0.4), relief=0.62, seed=seed)
    # a rim, and the specular streak that says "brass"
    p.rect(cx - w * 0.36, base_y - h * 1.02, w * 0.72, h * 0.10, shade(col, .18),
           light=(-0.7, -0.4), relief=0.3, seed=seed + 1)
    for k in range(7):
        p.dab(cx - w * 0.22, base_y - h * (0.38 + k * 0.055), max(2, w * 0.055),
              shade(col, 0.55), 0.30)


def kalasha(p, cx, base_y, s=1.0, seed=2):
    pot(p, cx, base_y, 44 * s, 56 * s, BRASS, seed)
    # five broad mango leaves fanning from the mouth
    mouth = (cx, base_y - 56 * s)
    for k, (ang, ln) in enumerate(((-158, 26), (-126, 32), (-90, 36), (-54, 32), (-22, 26))):
        a = math.radians(ang)
        col = LEAF_MID if k % 2 else LEAF_NEAR
        steps = 9
        for j in range(steps + 1):
            t = j / steps
            px = mouth[0] + math.cos(a) * ln * s * t
            py = mouth[1] + math.sin(a) * ln * s * t + (ln * s * 0.16) * t * t
            r = (8.2 * s) * (math.sin(math.pi * t ** 0.75) ** 0.45) + 1.6 * s
            p.dab(px, py, r, shade(col, 0.16 if k % 2 else -0.10), 0.95)
    p.dab(cx, base_y - 68 * s, 13 * s, (108, 72, 44), 0.95)          # coconut
    p.dab(cx - 4 * s, base_y - 72 * s, 6 * s, (152, 110, 72), 0.55)


def pillar(p, cx, top, bot, w, seed=3):
    p.shadow(cx, bot + 4, w * 1.5, 9, 0.5)
    p.rect(cx - w / 2, top, w, bot - top, GOLD, light=(-0.85, -0.25),
           relief=0.5, seed=seed)
    for y in (top, bot - w * 0.5):                      # capital and base
        p.rect(cx - w * 0.82, y, w * 1.64, w * 0.5, shade(GOLD, -0.18),
               light=(-0.85, -0.25), relief=0.42, seed=seed + 1)
    p.rect(cx - w * 0.16, top, w * 0.14, bot - top, shade(GOLD, 0.45),
           light=(0, 0), relief=0.0, seed=seed, edge=False)


def gopuram(p, cx, base_y, w, h, sky, tiers=12, depth=0.42):
    """A South Indian gopuram — tall and narrow, many shallow tiers, a gentle
    concave taper, and the barrel-vaulted cap on top."""
    col = mix((186, 150, 98), sky, depth)
    for i in range(tiers):
        t = i / tiers
        # concave profile: narrows fast low down, slows near the top
        tw = w * (1 - 0.52 * (t ** 0.78))
        th = h / tiers
        y = base_y - (i + 1) * th
        p.poly([(cx - tw / 2, y + th), (cx + tw / 2, y + th),
                (cx + tw * 0.465, y), (cx - tw * 0.465, y)],
               shade(col, 0.04 if i % 2 else -0.05),
               light=(-0.7, -0.4), relief=0.24, seed=10 + i)
        # thin cornice, not a ladder rung
        p.rect(cx - tw * 0.53, y, tw * 1.06, th * 0.16, shade(col, 0.20),
               light=(-0.7, -0.3), relief=0.18, seed=20 + i)
        if i < 4:                                   # shrine niches
            p.rect(cx - tw * 0.05, y + th * 0.30, tw * 0.10, th * 0.46,
                   mix((92, 34, 28), sky, depth), light=(0, 0), relief=0.1, seed=30 + i)
    # barrel-vaulted crown plus kalasha finials
    ty = base_y - h
    cw = w * (1 - 0.52)
    p.poly([(cx - cw * 0.46, ty), (cx + cw * 0.46, ty),
            (cx + cw * 0.30, ty - h * 0.07), (cx - cw * 0.30, ty - h * 0.07)],
           shade(col, 0.10), light=(-0.7, -0.4), relief=0.26, seed=44)
    for dx in (-cw * 0.28, 0, cw * 0.28):
        p.dab(cx + dx, ty - h * 0.085, 4.5, shade(col, 0.34), 0.95)


def curtain(p, x0, x1, top, length, step=13, seed=4):
    """Marigold strands hung as a backdrop."""
    rng = random.Random(seed)
    x = x0
    i = 0
    while x <= x1:
        L = length * (0.72 + 0.28 * math.sin(i * 0.7 + rng.random() * 0.3))
        p.stroke([(x, top), (x, top + L)], 1.6, LEAF_NEAR, 0.5)
        y = top + 5
        b = 0
        while y < top + L:
            r = rng.uniform(4.4, 6.4)
            base = MARI if b % 3 else MARI_D
            p.dab(x, y, r, base, 0.95)
            p.dab(x - r * 0.3, y - r * 0.3, r * 0.5, MARI_L, 0.6)
            y += r * 1.75
            b += 1
        x += step
        i += 1


def banana(p, x, base_y, size, seed=7, flip=False, depth=0.0, sky=None):
    """A banana clump.

    Banana leaves are broad drooping paddles, not spikes — so the dab radius
    follows a wide profile that stays fat most of the way out, the spine
    curves downward under its own weight, and each blade carries a midrib and
    a couple of the tears real banana leaves always have.
    """
    rng = random.Random(seed)
    spec = [(-146, .68), (-118, .90), (-92, 1.02), (-66, .92), (-38, .74)]
    for k, (ang, f) in enumerate(spec):
        a = math.radians(180 - ang if flip else ang)
        ln = size * f * rng.uniform(0.9, 1.1)
        tipx = x + math.cos(a) * ln
        tipy = base_y + math.sin(a) * ln + ln * 0.26          # droop
        midx = x + math.cos(a) * ln * 0.52
        midy = base_y + math.sin(a) * ln * 0.52 - ln * 0.05
        col = [LEAF_MID, LEAF_NEAR, LEAF_FAR][k % 3]
        if depth and sky:
            col = mix(col, sky, depth * 0.7)
        lit = 0.20 if (k % 2 == 0) else -0.16

        pts = []
        steps = 26
        for s in range(steps + 1):
            t = s / steps
            px = (1 - t) ** 2 * x + 2 * (1 - t) * t * midx + t * t * tipx
            py = (1 - t) ** 2 * base_y + 2 * (1 - t) * t * midy + t * t * tipy
            pts.append((px, py))
            # broad through the middle, tapering only near the very tip
            r = size * 0.20 * (math.sin(math.pi * t ** 0.8) ** 0.55) + 2.5
            p.dab(px, py, r, shade(col, lit * (1 - t * 0.35) + rng.uniform(-.06, .06)), 0.92)

        # midrib, then the tears
        p.stroke(pts, 1.6, shade(col, -0.34), 0.5)
        for tear in (0.42, 0.68):
            i = int(tear * steps)
            bx, by = pts[i]
            perp = a + math.pi / 2
            for s in range(5):
                d = s * size * 0.035
                p.dab(bx + math.cos(perp) * d, by + math.sin(perp) * d,
                      1.8, shade(col, -0.4), 0.35)


def ground(p, y, sky, seed=9, near=GRASS_NEAR, far=GRASS_FAR, depth=0.38):
    """A bank of grass, hazed at the back and dense in front."""
    rng = random.Random(seed)
    far_c = mix(far, sky, depth)
    p.poly([(0, y), (W, y - 6), (W, H), (0, H)], far_c,
           light=(-0.5, -0.7), relief=0.14, seed=seed)
    # scuff the horizon so it is not a ruled line
    for _ in range(260):
        ex = rng.uniform(-8, W + 8)
        ey = y - 6 * (ex / W) + rng.uniform(-9, 5)
        p.dab(ex, ey, rng.uniform(5, 12), shade(far_c, rng.uniform(-0.14, 0.18)),
              rng.uniform(0.2, 0.5))
    for _ in range(1400):
        t = rng.random() ** 0.7
        py = y + t * (H - y) + rng.uniform(-6, 6)
        px = rng.uniform(-10, W + 10)
        col = mix(far_c, near, t)
        p.dab(px, py, rng.uniform(5, 13), shade(col, rng.uniform(-0.16, 0.16)),
              rng.uniform(0.25, 0.6))


def diya(p, cx, base_y, s=1.0, bloom=1.0):
    p.glow(cx, base_y - 7 * s, 34 * s, (120, 78, 20), 0.5 * bloom)
    p.shadow(cx, base_y + 2 * s, 13 * s, 4 * s, 0.4)
    p.poly([(cx - 9 * s, base_y - 6 * s), (cx + 9 * s, base_y - 6 * s),
            (cx + 6 * s, base_y), (cx - 6 * s, base_y)], BRASS,
           light=(-0.7, -0.4), relief=0.4, seed=int(cx))
    p.dab(cx, base_y - 7 * s, 7 * s, BRASS_L, 0.75)
    p.dab(cx, base_y - 13 * s, 4.2 * s, FLAME, 0.95)
    p.dab(cx, base_y - 16 * s, 2.6 * s, (255, 246, 214), 0.95)
    p.glow(cx, base_y - 14 * s, 16 * s, (150, 104, 30), 0.75 * bloom)


def lamp_stand(p, cx, base_y, h, s=1.0, seed=11):
    p.shadow(cx, base_y + 3, 30 * s, 9 * s, 0.5)
    p.poly([(cx - 19 * s, base_y), (cx + 19 * s, base_y),
            (cx + 9 * s, base_y - 11 * s), (cx - 9 * s, base_y - 11 * s)], BRASS_D,
           light=(-0.8, -0.35), relief=0.45, seed=seed)
    p.rect(cx - 3.4 * s, base_y - h, 6.8 * s, h, BRASS,
           light=(-0.9, -0.2), relief=0.55, seed=seed + 1)
    p.rect(cx - 1.1 * s, base_y - h, 1.6 * s, h, shade(BRASS, 0.5),
           light=(0, 0), relief=0.0, seed=seed, edge=False)
    for k, fy in enumerate((0.32, 0.56, 0.78)):
        y = base_y - h * fy
        wdt = (19 - k * 3.4) * s
        p.poly([(cx - wdt, y), (cx + wdt, y), (cx + wdt * 0.6, y + 7 * s),
                (cx - wdt * 0.6, y + 7 * s)], BRASS_L,
               light=(-0.8, -0.35), relief=0.38, seed=seed + 5 + k)
        diya(p, cx - wdt * 0.62, y, s * 0.52, 0.8)
        diya(p, cx + wdt * 0.62, y, s * 0.52, 0.8)
    diya(p, cx, base_y - h, s * 0.8, 1.1)


def lantern(p, cx, top, drop, s=1.0):
    b = top + drop
    p.stroke([(cx, top), (cx, b - 9 * s)], 1.3, BRASS_D, 0.7)
    p.glow(cx, b + 9 * s, 52 * s, (140, 96, 28), 0.62)
    p.poly([(cx - 9 * s, b - 9 * s), (cx + 9 * s, b - 9 * s),
            (cx + 6 * s, b - 2 * s), (cx - 6 * s, b - 2 * s)], BRASS_D,
           light=(-0.7, -0.4), relief=0.4, seed=int(cx))
    p.dab(cx, b + 9 * s, 13 * s, (232, 168, 72), 0.92)
    p.dab(cx, b + 9 * s, 8.5 * s, FLAME, 0.95)
    p.dab(cx - 3 * s, b + 5 * s, 3.4 * s, (255, 250, 226), 0.85)
    p.poly([(cx - 5 * s, b + 20 * s), (cx + 5 * s, b + 20 * s), (cx, b + 27 * s)],
           BRASS_D, light=(-0.7, -0.4), relief=0.3, seed=int(cx) + 3)


def lotus(p, cx, cy, r):
    for k in range(9):
        a = math.tau * k / 9
        p.dab(cx + math.cos(a) * r * 0.62, cy + math.sin(a) * r * 0.5,
              r * 0.36, ROSE, 0.9)
    for k in range(6):
        a = math.tau * k / 6 + 0.4
        p.dab(cx + math.cos(a) * r * 0.34, cy + math.sin(a) * r * 0.28,
              r * 0.30, (232, 168, 180), 0.9)
    p.dab(cx, cy, r * 0.2, (246, 214, 120), 0.95)


# ================================================================ the scenes
def scene_dhare():
    sky = (246, 222, 198)
    p = Painting(W, H)
    p.haze(126, 362, sky, 0.0)                    # no-op base; sky comes from the card

    # distance
    for i in range(7):
        p.mass(59 + i * 93, 313, 77, 34, LEAF_MID, n=168, dab_r=13,
               seed=84 + i, depth=0.52, sky_rgb=sky, a=0.7)
    gopuram(p, 320, 338, 118, 214, sky, tiers=11, depth=0.16)

    ground(p, 333, sky, seed=9)

    # mandap
    BRONZE = (146, 96, 52)
    p.poly([(133, 226), (507, 226), (468, 204), (172, 204)], shade(BRONZE, -0.14),
           light=(-0.55, -0.7), relief=0.34, seed=34)          # upper slope
    p.poly([(108, 253), (532, 253), (507, 226), (133, 226)], BRONZE,
           light=(-0.6, -0.62), relief=0.30, seed=35)          # lower slope
    # tile courses, so the roof reads as a surface rather than a block
    for row, (ya, yb, xa, xb) in enumerate(((226, 253, 108, 532), (204, 226, 133, 507))):
        n = 5 if row == 0 else 4
        for k in range(1, n):
            t = k / n
            yy = ya + (yb - ya) * t
            inset = (xa - 108) + t * 22
            p.stroke([(xa + inset * 0.2, yy), (xb - inset * 0.2, yy)], 1.5,
                     shade(BRONZE, -0.30), 0.45)
    for k in range(39):                                        # pantile ribs
        xx = 111 + k * 11
        p.stroke([(xx, 253), (xx + 7, 226)], 1.3, shade(BRONZE, -0.22), 0.28)
    p.rect(101, 249, 438, 7, shade(GOLD, 0.20), light=(0, 0), relief=0.0,
           seed=35, edge=False)                                 # eave highlight
    p.rect(118, 255, 404, 14, shade(GOLD, -0.05), light=(-0.7, -0.35), relief=0.44, seed=35)

    curtain(p, 173, 468, 266, 72, step=12, seed=4)

    pillar(p, 145, 221, 340, 25, seed=43)
    pillar(p, 495, 221, 340, 25, seed=44)

    kalasha(p, 199, 340, 1.0, seed=51)
    kalasha(p, 441, 340, 1.0, seed=52)
    for x in (278, 320, 362):
        diya(p, x, 362, 0.9)

    banana(p, 29, 367, 118, seed=60)
    banana(p, 611, 367, 118, seed=61, flip=True)
    banana(p, 91, 381, 81, seed=61)
    banana(p, 549, 381, 81, seed=62, flip=True)
    return p


def scene_haldi():
    sky = (250, 232, 198)
    p = Painting(W, H)

    for i in range(6):
        p.mass(51 + i * 111, 310, 84, 32, LEAF_MID, n=143, dab_r=13,
               seed=168 + i, depth=0.55, sky_rgb=sky, a=0.65)

    # the marigold backdrop wall
    p.rect(126, 71, 389, 9, WOOD, light=(-0.6, -0.5), relief=0.35, seed=68)
    curtain(p, 133, 509, 79, 195, step=12, seed=5)

    ground(p, 330, sky, seed=12)

    # low seat
    p.shadow(320, 342, 93, 16, 0.45)
    p.rect(261, 290, 120, 17, WOOD, light=(-0.7, -0.4), relief=0.36, seed=69)
    p.rect(261, 290, 120, 5, shade(WOOD, 0.4), light=(0, 0), relief=0.0, seed=69, edge=False)
    for lx in (271, 362):
        p.rect(lx, 304, 11, 37, shade(WOOD, -0.22), light=(-0.7, -0.4), relief=0.3, seed=70)
    for k in range(22):                                    # petals on the seat
        p.dab(266 + k * 5.4, 290 + math.sin(k) * 1.6, 4.6, MARI_L, 0.55)

    for x in (88, 126, 165):
        pot(p, x, 340, 34, 44, BRASS, seed=int(x))
    for x in (475, 514, 552):
        pot(p, x, 340, 34, 44, BRASS, seed=int(x))

    for x, s in ((280, 1.0), (320, 1.18), (360, 1.0)):      # turmeric plates
        p.shadow(x, 352, 22 * s, 8 * s, 0.4)
        p.poly([(x - 20 * s, 349), (x + 20 * s, 349), (x + 19 * s, 355), (x - 19 * s, 355)],
               BRASS_L, light=(-0.7, -0.4), relief=0.35, seed=int(x))
        p.dab(x, 347, 16 * s, (226, 164, 40), 0.95)
        p.dab(x - 4 * s, 344, 8 * s, (244, 198, 76), 0.7)

    banana(p, 27, 362, 111, seed=77)
    banana(p, 613, 362, 111, seed=77, flip=True)
    return p


def scene_mehendi():
    sky = (206, 198, 168)
    p = Painting(W, H)

    for i in range(7):
        p.mass(42 + i * 99, 301, 88, 39, LEAF_MID, n=185, dab_r=14,
               seed=253 + i, depth=0.5, sky_rgb=sky, a=0.72)

    ground(p, 332, sky, seed=15, near=(40, 68, 46), far=(88, 116, 76), depth=0.42)

    # a patterned screen behind the seating
    p.rect(162, 195, 317, 103, (72, 96, 68), light=(-0.5, -0.5), relief=0.22, seed=85)
    p.rect(162, 190, 317, 10, shade(WOOD, -0.1), light=(-0.6, -0.4), relief=0.3, seed=86)
    rng = random.Random(4)
    for i in range(11):
        x = 179 + i * 28
        for k in range(9):
            t = k / 8
            p.dab(x + math.sin(t * 3.1) * 9, 211 + t * 77, 4.6,
                  shade(CREAMY, -0.05), 0.28 + rng.random() * 0.12)

    # divan
    p.shadow(320, 344, 111, 16, 0.45)
    for cxp, col in ((221, ROSE), (263, (222, 150, 166)), (377, ROSE), (419, (222, 150, 166))):
        p.dab(cxp, 253, 18, col, 0.95)
        p.dab(cxp - 5, 248, 13, shade(col, 0.3), 0.7)
    p.rect(205, 263, 229, 19, WOOD, light=(-0.7, -0.4), relief=0.36, seed=87)
    p.rect(205, 263, 229, 6, shade(WOOD, 0.4), light=(0, 0), relief=0.0, seed=87, edge=False)
    for lx in (216, 416):
        p.rect(lx, 281, 13, 29, shade(WOOD, -0.22), light=(-0.7, -0.4), relief=0.3, seed=88)

    # brass tray with henna cones
    p.shadow(320, 352, 29, 9, 0.4)
    p.poly([(293, 344), (347, 344), (340, 352), (300, 352)], BRASS_L,
           light=(-0.7, -0.4), relief=0.35, seed=88)
    for dx in (-11, 0, 11):
        p.poly([(320 + dx - 4, 344), (320 + dx + 4, 344), (320 + dx, 327)],
               LEAF_NEAR, light=(-0.7, -0.4), relief=0.3, seed=89 + dx)

    for cx, drop, s in ((81, 108, 1.05), (165, 150, 0.85), (475, 140, 0.9), (559, 101, 1.1)):
        lantern(p, cx, 34, drop, s)

    banana(p, 24, 364, 116, seed=93)
    banana(p, 616, 364, 116, seed=94, flip=True)
    banana(p, 94, 377, 79, seed=95)
    banana(p, 546, 377, 79, seed=96, flip=True)
    for x in (126, 165, 475, 514):
        diya(p, x, 367, 0.8)
    return p


def scene_lamp():
    sky = (96, 118, 122)
    p = Painting(W, H)

    for i in range(7):
        p.mass(42 + i * 99, 286, 91, 37, (34, 62, 56), n=200, dab_r=14,
               seed=337 + i, depth=0.45, sky_rgb=sky, a=0.75)

    ground(p, 283, sky, seed=18, near=(20, 44, 40), far=(44, 74, 66), depth=0.4)

    lamp_stand(p, 94, 328, 190, 1.25, seed=102)
    lamp_stand(p, 546, 328, 190, 1.25, seed=103)
    lamp_stand(p, 182, 323, 138, 0.95, seed=104)
    lamp_stand(p, 458, 323, 138, 0.95, seed=104)

    # garland swags between the stands
    rng = random.Random(6)
    for (x0, x1, y, sag, r) in ((109, 532, 190, 32, 6.6), (195, 445, 241, 22, 5.6)):
        n = int((x1 - x0) / 7)
        for i in range(n + 1):
            t = i / n
            gx = x0 + (x1 - x0) * t
            gy = y + sag * math.sin(math.pi * t) ** 0.9
            p.dab(gx, gy, r * rng.uniform(0.8, 1.15), MARI if i % 3 else MARI_D, 0.95)
            p.dab(gx - r * 0.3, gy - r * 0.3, r * 0.45, MARI_L, 0.5)

    for i in range(15):
        diya(p, 19 + i * 43, 340, 0.95)

    # the pond
    p.poly([(0, 362), (W, 357), (W, H), (0, H)], (26, 58, 62),
           light=(-0.4, -0.8), relief=0.2, seed=110)
    for _ in range(160):                       # broken waterline
        ex = rng.uniform(-8, W + 8)
        ey = 362 - 6 * (ex / W) + rng.uniform(-7, 6)
        p.dab(ex, ey, rng.uniform(5, 13), shade((32, 66, 66), rng.uniform(-0.15, 0.2)),
              rng.uniform(0.2, 0.45))
    for i in range(9):                                     # reflected light
        p.glow(19 + i * 74, 381, 39, (70, 52, 16), 0.34)
    for x in (61, 180, 320, 460, 581):
        p.dab(x, 394, 20, (30, 70, 64), 0.5)
        p.dab(x, 392, 17, (40, 88, 74), 0.4)
    for cx, s in ((116, 1.0), (253, 0.85), (320, 1.3), (396, 0.85), (522, 1.0)):
        lotus(p, cx, 389, 18 * s)
    return p


# ================================================================ write all
if __name__ == "__main__":
    print("painting scenes...")
    for name, fn in (("dhare", scene_dhare), ("haldi", scene_haldi),
                     ("mehendi", scene_mehendi), ("lamp", scene_lamp)):
        pic = fn()
        pic.fade_top(0.15, 1.4)
        pic.save(OUT + "scene-" + name + ".png", rgba=True)
    print("done.")
