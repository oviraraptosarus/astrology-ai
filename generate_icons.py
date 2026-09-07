"""Generate PWA icons for Astrology AI (no external assets, pure PIL).

Creates a calm, premium mark: a soft radial night-sky disc with a single
minimal crescent + one star — no purple neon, no clutter. Produces standard
and maskable variants at 192 and 512.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(__file__), "static", "icons")
os.makedirs(OUT, exist_ok=True)

BG_TOP = (24, 24, 34)       # near-black indigo
BG_BOT = (11, 11, 15)       # near-black
MOON = (245, 244, 250)      # soft white
ACCENT = (150, 170, 255)    # subtle celestial blue (not neon purple)


def _radial_bg(size, pad_ratio=0.0):
    img = Image.new("RGB", (size, size), BG_BOT)
    px = img.load()
    cx = cy = size / 2
    maxd = size * 0.72
    for y in range(size):
        for x in range(size):
            d = math.hypot(x - cx, y - cy) / maxd
            d = min(1.0, d)
            r = int(BG_TOP[0] * (1 - d) + BG_BOT[0] * d)
            g = int(BG_TOP[1] * (1 - d) + BG_BOT[1] * d)
            b = int(BG_TOP[2] * (1 - d) + BG_BOT[2] * d)
            px[x, y] = (r, g, b)
    return img


def _draw_mark(img, size, inset=0.0):
    """Minimal crescent moon + a single small star, centered."""
    ss = 4  # supersample
    layer = Image.new("RGBA", (size * ss, size * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    S = size * ss
    cx = cy = S / 2
    r = S * (0.30 - inset)  # moon radius

    # Full moon disc
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=MOON + (255,))
    # Subtract an offset disc to carve the crescent
    off = r * 0.55
    cr = r * 1.02
    d.ellipse([cx - cr + off, cy - cr - off * 0.15, cx + cr + off, cy + cr - off * 0.15],
              fill=(0, 0, 0, 0))
    # Re-carve using a mask so we truly subtract (paste transparent)
    mask = Image.new("L", (S, S), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    md.ellipse([cx - cr + off, cy - cr - off * 0.15, cx + cr + off, cy + cr - off * 0.15], fill=0)
    moon_layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    moon_solid = Image.new("RGBA", (S, S), MOON + (255,))
    moon_layer = Image.composite(moon_solid, moon_layer, mask)

    # A single small star, upper-right of the crescent opening
    star_layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sd = ImageDraw.Draw(star_layer)
    sx, sy = cx + r * 0.75, cy - r * 0.62
    sr = r * 0.12
    _star(sd, sx, sy, sr, ACCENT + (255,))

    combined = Image.alpha_composite(moon_layer, star_layer)
    combined = combined.resize((size, size), Image.LANCZOS)
    img = img.convert("RGBA")
    img.alpha_composite(combined)
    return img.convert("RGB")


def _star(draw, cx, cy, r, fill, points=4):
    pts = []
    for i in range(points * 2):
        ang = math.pi * i / points - math.pi / 2
        rad = r if i % 2 == 0 else r * 0.38
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    draw.polygon(pts, fill=fill)


def make(size, maskable=False):
    img = _radial_bg(size)
    if maskable:
        # Maskable: keep the mark inside the safe zone (~80%); background fills edges.
        img = _draw_mark(img, size, inset=0.06)
    else:
        img = _draw_mark(img, size, inset=0.0)
    return img


for size in (192, 512):
    make(size, maskable=False).save(os.path.join(OUT, f"icon-{size}.png"))
    make(size, maskable=True).save(os.path.join(OUT, f"icon-maskable-{size}.png"))

# Apple touch icon (180) — no transparency, rounded handled by iOS.
make(180, maskable=False).save(os.path.join(OUT, "apple-touch-icon.png"))
# Favicon
make(64, maskable=False).save(os.path.join(OUT, "favicon-64.png"))

print("Icons written to", OUT)
for f in sorted(os.listdir(OUT)):
    print(" ", f)
