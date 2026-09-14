#!/usr/bin/env python3
"""Regenerate assets/img/og-image.png — the WhatsApp / Facebook share card.

Reads the names, date and venue straight out of assets/js/data.js, so the card
never drifts from the site.

    python3 tools/make_share_card.py

macOS only: it renders the card with QuickLook (`qlmanage`), which is the one
HTML renderer present on a stock Mac. Needs an internet connection the first
time, to fetch the Google Fonts.

Everything else is pure stdlib.
"""
import os, re, sys, json, zlib, struct, subprocess, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, "tools", "share-card.html")
STAGED = os.path.join(ROOT, "_share-card.html")     # must sit at the project
OUT = os.path.join(ROOT, "assets", "img", "og-image.png")  # root for relative paths
TMP = "/tmp/_sharecard_render"


# --------------------------------------------------------------- read data.js
def load_invite():
    dump = "/tmp/_invite_data.json"
    js = ("ObjC.import('Foundation');\n"
          "function read(p){return $.NSString.stringWithContentsOfFileEncodingError("
          "p,$.NSUTF8StringEncoding,null).js;}\n"
          "var D = new Function(read(%s) + '; return INVITE;')();\n"
          "$.NSString.alloc.initWithUTF8String(JSON.stringify(D))"
          ".writeToFileAtomicallyEncodingError(%s, true, $.NSUTF8StringEncoding, null);\n"
          % (json.dumps(os.path.join(ROOT, "assets/js/data.js")), json.dumps(dump)))
    open("/tmp/_invite_dump.js", "w").write(js)
    subprocess.check_call(["osascript", "-l", "JavaScript", "/tmp/_invite_dump.js"])
    return json.load(open(dump))


# --------------------------------------------------------------- PNG helpers
def read_png(path):
    data = open(path, "rb").read()
    pos, idat = 8, []
    while pos < len(data):
        ln = struct.unpack(">I", data[pos:pos + 4])[0]
        tag = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + ln]
        if tag == b"IHDR":
            w, h, depth, ctype = struct.unpack(">IIBB", body[:10])
        elif tag == b"IDAT":
            idat.append(body)
        elif tag == b"IEND":
            break
        pos += 12 + ln
    raw = zlib.decompress(b"".join(idat))
    nch = 3 if ctype == 2 else 4
    stride = w * nch
    out, prev, p = bytearray(), bytearray(stride), 0
    for _ in range(h):
        f = raw[p]; p += 1
        line = bytearray(raw[p:p + stride]); p += stride
        for i in range(stride):
            a = line[i - nch] if i >= nch else 0
            b = prev[i]
            c = prev[i - nch] if i >= nch else 0
            if f == 1:   line[i] = (line[i] + a) & 255
            elif f == 2: line[i] = (line[i] + b) & 255
            elif f == 3: line[i] = (line[i] + (a + b) // 2) & 255
            elif f == 4:
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        out += line
        prev = line
    return w, h, nch, bytes(out)


def write_png(path, w, h, nch, px):
    raw = b"".join(b"\x00" + px[y * w * nch:(y + 1) * w * nch] for y in range(h))
    def chunk(tag, d):
        return struct.pack(">I", len(d)) + tag + d + struct.pack(">I", zlib.crc32(tag + d) & 0xffffffff)
    blob = (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2 if nch == 3 else 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    open(path, "wb").write(blob)
    return len(blob)


# --------------------------------------------------------------- go
def main():
    if not shutil.which("qlmanage"):
        sys.exit("qlmanage not found — this script needs macOS.")

    D = load_invite()
    html = open(TEMPLATE).read()
    for slot, value in (
        ("{{INVOCATION}}", D["words"]["invocation"]),
        ("{{BRIDE}}", D["bride"]["name"]),
        ("{{GROOM}}", D["groom"]["name"]),
        ("{{DATE}}", D["dateLine"]),
        ("{{VENUE}}", D["venue"].get("short") or D["venue"]["name"]),
    ):
        html = html.replace(slot, value)

    open(STAGED, "w").write(html)
    try:
        shutil.rmtree(TMP, ignore_errors=True)
        os.makedirs(TMP)
        subprocess.run(["qlmanage", "-t", "-s", "1200", "-o", TMP, STAGED],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        shot = os.path.join(TMP, os.path.basename(STAGED) + ".png")
        if not os.path.exists(shot):
            sys.exit("QuickLook produced no image — try again, it is occasionally flaky.")

        w, h, nch, px = read_png(shot)

        # QuickLook pads the thumbnail to a square and scales to its own
        # viewport width, so find the magenta edge markers and cut to the card.
        def magenta(x, y):
            i = (y * w + x) * nch
            return px[i] > 200 and px[i + 1] < 90 and px[i + 2] > 200

        bottom = next(y for y in range(h - 1, -1, -1)
                      if sum(1 for x in range(0, w, 7) if magenta(x, y)) > (w // 7) * 0.4)
        right = next(x for x in range(w - 1, -1, -1)
                     if sum(1 for y in range(0, bottom, 7) if magenta(x, y)) > (bottom // 7) * 0.4)
        cw, ch = right - 4, bottom - 4

        rows = bytearray()
        for y in range(ch):
            rows += px[(y * w) * nch:(y * w + cw) * nch]
        size = write_png(OUT, cw, ch, nch, bytes(rows))
        print("og-image.png  %dx%d  aspect %.3f  %.0f KB" % (cw, ch, cw / ch, size / 1024))
        print("Remember to update the og: meta tags in index.html too.")
    finally:
        if os.path.exists(STAGED):
            os.remove(STAGED)
        shutil.rmtree(TMP, ignore_errors=True)


if __name__ == "__main__":
    main()
