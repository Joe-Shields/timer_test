"""Generate PWA icons for the Time Debt Clock app.

Design matches the app palette:
  bg #0a0e14, clock ring #3b82f6, hands #22d3ee/#e8eefc,
  green "debt" arc hsl(120 70% 52%) ~= #2fd92f.

Run:  python make_icons.py
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent / "icons"
BG = (10, 14, 20, 255)
BORDER = (38, 49, 74, 255)
BLUE = (59, 130, 246, 255)
CYAN = (34, 211, 238, 255)
INK = (232, 238, 252, 255)
GREEN = (47, 217, 47, 255)  # hsl(120 70% 52%)


def draw_icon(size: int, maskable: bool = False) -> Image.Image:
    s = size * 4  # supersample for antialiasing
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    if maskable:
        d.rectangle([0, 0, s, s], fill=BG)
        radius = s * 0.30  # keep art inside the 80% maskable safe zone
    else:
        d.rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * 0.18), fill=BG)
        d.rounded_rectangle(
            [0, 0, s - 1, s - 1], radius=int(s * 0.18),
            outline=BORDER, width=max(2, s // 120),
        )
        radius = s * 0.34

    cx = cy = s / 2
    lw = max(4, int(s * 0.055))

    # Outer green arc (the "debt" timer), 270 degrees starting at 12 o'clock.
    arc_r = radius + lw * 1.15
    d.arc(
        [cx - arc_r, cy - arc_r, cx + arc_r, cy + arc_r],
        start=-90, end=180, fill=GREEN, width=lw,
    )

    # Main clock ring.
    d.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
              outline=BLUE, width=lw)

    # Hands: minute hand to 12, hour hand to ~4:30.
    hand_w = max(3, int(s * 0.035))
    d.line([cx, cy, cx, cy - radius * 0.72], fill=CYAN, width=hand_w)
    ang = math.radians(45)
    d.line([cx, cy,
            cx + radius * 0.5 * math.sin(ang),
            cy + radius * 0.5 * math.cos(ang)],
           fill=INK, width=hand_w)

    # Center hub.
    cr = hand_w * 0.9
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=CYAN)

    return img.resize((size, size), Image.LANCZOS)


def load_font(size: int):
    for name in ("arialbd.ttf", "arial.ttf", "segoeui.ttf", "verdanab.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_screenshot(w: int = 1280, h: int = 720) -> Image.Image:
    img = Image.new("RGBA", (w, h), BG)
    d = ImageDraw.Draw(img)
    pad = int(w * 0.035)

    # Toolbar
    tb_h = int(h * 0.11)
    d.rounded_rectangle([pad, pad, w - pad, pad + tb_h], radius=tb_h // 3,
                        fill=(17, 24, 34, 255), outline=BORDER, width=2)
    tb_font = load_font(int(tb_h * 0.42))
    d.text((pad + tb_h * 0.5, pad + tb_h * 0.5), "TIME DEBT CLOCK",
           fill=INK, font=tb_font, anchor="mm")

    # Two player cards
    top = pad * 2 + tb_h
    bottom = h - pad
    gap = pad
    card_w = (w - pad * 2 - gap) // 2
    card_h = bottom - top
    radii = [10, 7, 4]
    for i, (x0, accent) in enumerate([(pad, BLUE), (pad * 2 + card_w, GREEN)]):
        d.rounded_rectangle([x0, top, x0 + card_w, bottom], radius=int(w * 0.02),
                            fill=(17, 24, 34, 255), outline=accent, width=3)
        # lives
        lr = int(w * 0.011)
        for k in range(3):
            lx = x0 + int(card_w * 0.12) + k * (lr * 3)
            d.ellipse([lx - lr, top + lr * 2 - lr, lx + lr, top + lr * 2 + lr],
                      fill=(accent[0], accent[1], accent[2], 220))
        # HP bar
        bar_x0, bar_x1 = x0 + int(card_w * 0.08), x0 + int(card_w * 0.92)
        bar_y = top + int(card_h * 0.16)
        d.rounded_rectangle([bar_x0, bar_y, bar_x1, bar_y + int(h * 0.022)],
                            radius=int(h * 0.011), fill=(20, 28, 40, 255))
        d.rounded_rectangle([bar_x0, bar_y,
                             bar_x1 - (0 if i == 0 else int(card_w * 0.25)),
                             bar_y + int(h * 0.022)],
                            radius=int(h * 0.011), fill=accent)
        # big timer
        d.text((x0 + card_w // 2, top + int(card_h * 0.46)),
               "03:45.2" if i == 0 else "05:12.8",
               fill=INK, font=load_font(int(card_h * 0.30)), anchor="mm")
        # threshold ring
        ring_cx, ring_cy = x0 + card_w // 2, top + int(card_h * 0.80)
        ring_r = int(card_h * 0.13)
        lw = max(4, int(w * 0.006))
        d.ellipse([ring_cx - ring_r, ring_cy - ring_r, ring_cx + ring_r, ring_cy + ring_r],
                  outline=BORDER, width=lw)
        d.arc([ring_cx - ring_r, ring_cy - ring_r, ring_cx + ring_r, ring_cy + ring_r],
              start=-90, end=-90 + 250, fill=accent, width=lw)
        d.text((ring_cx, ring_cy), "10", fill=INK,
               font=load_font(int(ring_r * 0.9)), anchor="mm")
        # threshold ticks
        tick_font = load_font(int(card_h * 0.045))
        for j, r in enumerate(radii):
            d.text((x0 + int(card_w * (0.16 + 0.12 * j)), top + int(card_h * 0.94)),
                   str(r), fill=(150, 165, 195, 255), font=tick_font, anchor="mm")

    img = img.convert("RGB")
    img.save(OUT / "screenshot-wide.png")
    print(f"wrote icons/screenshot-wide.png ({w}x{h})")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [
        ("icon-192.png", 192, False),
        ("icon-512.png", 512, False),
        ("icon-maskable-192.png", 192, True),
        ("icon-maskable-512.png", 512, True),
        ("apple-touch-icon-180.png", 180, True),  # iOS wants opaque full-bleed
    ]
    for name, size, maskable in jobs:
        draw_icon(size, maskable).save(OUT / name)
        print(f"wrote icons/{name} ({size}x{size})")
    draw_screenshot()


if __name__ == "__main__":
    main()
