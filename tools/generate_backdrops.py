"""Paint the section backdrops.

The interior sections were flat cream bands. These replace them with painted
fields — each with its own temperature, so scrolling the page moves through a
sequence of related colours instead of one uniform wash.

Kept deliberately pale and low-contrast: text sits on top of these.

    python3 tools/generate_backdrops.py
"""

import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paint import Painting                                   # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "assets", "img") + os.sep

W, H = 440, 600          # soft content upscales cleanly, so these stay small

# ---------------------------------------------------------------- palette
IVORY   = (253, 248, 238)
CREAM   = (249, 241, 226)
CHAMP   = (245, 234, 212)
BLUSH   = (243, 224, 212)
PEACH   = (245, 227, 202)
SAGE    = (226, 230, 210)
ROSEP   = (243, 223, 221)
GOLDP   = (242, 230, 198)


def backdrop(name, stops, blooms, seed):
    """stops: vertical ramp. blooms: (fx, fy, frx, fry, colour, alpha)."""
    p = Painting(W, H)
    p.sky(stops, warp_seed=seed, warp=0.10, mottle=0.12)
    for i, (fx, fy, frx, fry, col, a) in enumerate(blooms):
        # light=(0,0) means no directional shading: on a pale field the violet
        # shadow side of a lit clump reads as a dirty stain, not as colour.
        # Few, very large, very faint dabs give drift instead of blotches.
        p.mass(fx * W, fy * H, frx * W, fry * H, col,
               n=46, dab_r=int(W * 0.24), jitter=0.03,
               light=(0, 0), seed=seed * 31 + i, a=a * 0.42)
    p.vignette(0.10)
    # no baked grain — the page already lays one over everything in CSS, and
    # baking a second only defeats PNG compression
    p.save(OUT + "bg-" + name + ".png")


if __name__ == "__main__":
    print("painting section backdrops...")

    # countdown — warm champagne, the page's first interior breath
    backdrop("countdown",
             [(0.0, IVORY), (0.45, CHAMP), (1.0, PEACH)],
             [(0.22, 0.28, 0.42, 0.30, BLUSH, 0.30),
              (0.80, 0.66, 0.38, 0.28, GOLDP, 0.32),
              (0.50, 0.94, 0.55, 0.22, PEACH, 0.30)],
             seed=21)

    # invitation — the palest of the set, so the wording carries it
    backdrop("invitation",
             [(0.0, IVORY), (0.5, IVORY), (1.0, CREAM)],
             [(0.26, 0.34, 0.40, 0.30, SAGE, 0.22),
              (0.78, 0.72, 0.40, 0.28, CHAMP, 0.30)],
             seed=22)

    # families — a soft rose turn
    backdrop("families",
             [(0.0, CREAM), (0.5, ROSEP), (1.0, CHAMP)],
             [(0.18, 0.24, 0.44, 0.30, BLUSH, 0.34),
              (0.84, 0.60, 0.40, 0.30, IVORY, 0.30),
              (0.44, 0.92, 0.55, 0.22, CHAMP, 0.30)],
             seed=23)

    # events — warmest, the painted cards sit on this
    backdrop("events",
             [(0.0, CHAMP), (0.42, PEACH), (1.0, CREAM)],
             [(0.30, 0.20, 0.46, 0.26, GOLDP, 0.34),
              (0.74, 0.70, 0.42, 0.30, BLUSH, 0.30)],
             seed=24)

    # venue — cools back down toward sage before the maroon closing
    backdrop("venue",
             [(0.0, CREAM), (0.48, SAGE), (1.0, IVORY)],
             [(0.24, 0.30, 0.42, 0.28, IVORY, 0.34),
              (0.80, 0.68, 0.40, 0.30, CHAMP, 0.30)],
             seed=25)

    print("done.")
