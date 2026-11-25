#!/usr/bin/env python3
"""
Generates high-resolution 4K (3840x2160) minimalist & Apple-inspired wallpapers for Jarvis OS:
1. Jarvis Zen: Minimalist Dark Slate / Charcoal aesthetic (Pop!_OS / Ubuntu inspired).
2. Jarvis Cyber: Obsidian / Electric Cyan HUD aesthetic.
3. Jarvis Cupertino Dark: Apple macOS Sequoia/Tahoe deep emerald/indigo fluid wave mesh.
4. Jarvis Cupertino Light: Apple macOS Sonoma/Sequoia pearl pastel fluid wave mesh.
5. Jarvis Nordic: Arctic polar frost geometric slate with aurora ribbon.
"""

import os
import math
import json
from PIL import Image, ImageDraw, ImageFilter

WIDTH = 3840
HEIGHT = 2160


def _save_png(img: Image.Image, output_path: str, label: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.convert("RGB").save(output_path, "PNG", optimize=True)
    print(f"[OK] Generated {label} wallpaper: {output_path}")


def create_zen_wallpaper(output_path: str):
    """Generates the Zen Minimalist wallpaper."""
    img = Image.new("RGBA", (WIDTH, HEIGHT), (24, 25, 38, 255))
    draw = ImageDraw.Draw(img)

    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(30 * (1 - ratio) + 20 * ratio)
        g = int(32 * (1 - ratio) + 22 * ratio)
        b = int(48 * (1 - ratio) + 34 * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255))

    poly1 = [(0, int(HEIGHT * 0.65)), (int(WIDTH * 0.45), HEIGHT), (0, HEIGHT)]
    draw.polygon(poly1, fill=(28, 30, 46, 160))

    poly2 = [(WIDTH, int(HEIGHT * 0.25)), (WIDTH, HEIGHT), (int(WIDTH * 0.55), HEIGHT)]
    draw.polygon(poly2, fill=(20, 22, 34, 180))

    draw.line([(WIDTH, int(HEIGHT * 0.25)), (int(WIDTH * 0.55), HEIGHT)], fill=(137, 180, 250, 45), width=2)
    draw.line([(0, int(HEIGHT * 0.65)), (int(WIDTH * 0.45), HEIGHT)], fill=(137, 180, 250, 35), width=2)

    cx, cy = WIDTH // 2, HEIGHT // 2
    draw.ellipse([cx - 180, cy - 180, cx + 180, cy + 180], outline=(147, 153, 178, 40), width=2)
    draw.ellipse([cx - 120, cy - 120, cx + 120, cy + 120], outline=(180, 190, 254, 60), width=1)
    draw.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=(137, 180, 250, 80))
    draw.line([(cx - 360, cy), (cx - 220, cy)], fill=(147, 153, 178, 40), width=1)
    draw.line([(cx + 220, cy), (cx + 360, cy)], fill=(147, 153, 178, 40), width=1)

    _save_png(img, output_path, "Zen")


def create_cyber_wallpaper(output_path: str):
    """Generates the Cyber HUD Obsidian wallpaper."""
    img = Image.new("RGBA", (WIDTH, HEIGHT), (9, 11, 16, 255))
    draw = ImageDraw.Draw(img)

    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(12 * (1 - ratio) + 7 * ratio)
        g = int(16 * (1 - ratio) + 9 * ratio)
        b = int(24 * (1 - ratio) + 14 * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255))

    grid_size = 120
    for x in range(0, WIDTH, grid_size):
        draw.line([(x, 0), (x, HEIGHT)], fill=(0, 229, 255, 12), width=1)
    for y in range(0, HEIGHT, grid_size):
        draw.line([(0, y), (WIDTH, y)], fill=(0, 229, 255, 12), width=1)

    cx, cy = WIDTH // 2, HEIGHT // 2
    draw.ellipse([cx - 480, cy - 480, cx + 480, cy + 480], outline=(0, 229, 255, 30), width=1)
    num_ticks = 72
    for i in range(num_ticks):
        angle = 2 * math.pi * i / num_ticks
        inner_r = 460 if i % 6 == 0 else 470
        x1 = cx + inner_r * math.cos(angle)
        y1 = cy + inner_r * math.sin(angle)
        x2 = cx + 480 * math.cos(angle)
        y2 = cy + 480 * math.sin(angle)
        color = (0, 229, 255, 180) if i % 6 == 0 else (0, 229, 255, 60)
        draw.line([(x1, y1), (x2, y2)], fill=color, width=2 if i % 6 == 0 else 1)

    draw.ellipse([cx - 360, cy - 360, cx + 360, cy + 360], outline=(0, 229, 255, 70), width=3)
    draw.ellipse([cx - 240, cy - 240, cx + 240, cy + 240], outline=(0, 255, 200, 100), width=2)
    draw.ellipse([cx - 140, cy - 140, cx + 140, cy + 140], outline=(0, 229, 255, 140), width=2)
    draw.ellipse([cx - 60, cy - 60, cx + 60, cy + 60], fill=(0, 229, 255, 90), outline=(0, 255, 255, 220), width=2)

    draw.line([(cx - 600, cy), (cx - 380, cy)], fill=(0, 229, 255, 120), width=1)
    draw.line([(cx + 380, cy), (cx + 600, cy)], fill=(0, 229, 255, 120), width=1)
    draw.line([(cx, cy - 600), (cx, cy - 380)], fill=(0, 229, 255, 120), width=1)
    draw.line([(cx, cy + 380), (cx, cy + 600)], fill=(0, 229, 255, 120), width=1)

    _save_png(img, output_path, "Cyber")


def create_cupertino_wallpaper(output_path: str, dark: bool = True):
    """Generates an Apple macOS-inspired soft fluid mesh gradient wallpaper at 4K."""
    # Render downscaled smooth gradient mesh, then upscale cleanly with bicubic + Gaussian blur
    sw, sh = 960, 540
    base_bg = (16, 18, 28, 255) if dark else (238, 241, 248, 255)
    img = Image.new("RGBA", (sw, sh), base_bg)
    draw = ImageDraw.Draw(img)

    # Smooth base vertical gradient
    for y in range(sh):
        t = y / sh
        if dark:
            c = (int(14 + 12 * t), int(18 + 16 * t), int(34 + 28 * t), 255)
        else:
            c = (int(242 - 14 * t), int(245 - 8 * t), int(252 - 4 * t), 255)
        draw.line([(0, y), (sw, y)], fill=c)

    # Organic Apple-like silky curved color ribbons
    blobs = (
        [
            ((180, 120), 260, (10, 132, 255, 165)),    # Apple Blue
            ((480, 280), 310, (48, 209, 88, 125)),     # Emerald Mint
            ((740, 160), 280, (94, 92, 230, 150)),     # Deep Indigo
            ((620, 420), 240, (100, 210, 255, 110)),   # Cyan Frost
        ]
        if dark else
        [
            ((200, 140), 290, (100, 210, 255, 175)),   # Sky Azure
            ((520, 280), 320, (125, 225, 185, 145)),   # Pastel Mint
            ((760, 180), 280, (175, 165, 255, 155)),   # Soft Iris
            ((400, 420), 260, (255, 195, 160, 110)),   # Warm Pearl Coral
        ]
    )

    overlay = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    for (cx, cy), rad, color in blobs:
        odraw.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=color)

    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=95))
    img = Image.alpha_composite(img, overlay)

    # Crisp diagonal satin wave highlight
    wave = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    wdraw = ImageDraw.Draw(wave)
    pts = []
    for x in range(0, sw + 20, 20):
        y = int(sh * 0.52 + math.sin(x / 180.0) * 85 - (x - sw / 2) * 0.14)
        pts.append((x, y))
    pts.extend([(sw, sh), (0, sh)])
    wdraw.polygon(pts, fill=(255, 255, 255, 18 if dark else 95))
    wave = wave.filter(ImageFilter.GaussianBlur(radius=18))
    img = Image.alpha_composite(img, wave)

    # Upscale to 4K cleanly
    img_4k = img.resize((WIDTH, HEIGHT), Image.Resampling.BICUBIC)
    _save_png(img_4k, output_path, "Cupertino Dark" if dark else "Cupertino Light")


def create_nordic_wallpaper(output_path: str):
    """Generates the Nordic Arctic minimal geometric wallpaper."""
    sw, sh = 960, 540
    img = Image.new("RGBA", (sw, sh), (46, 52, 64, 255))
    draw = ImageDraw.Draw(img)

    for y in range(sh):
        t = y / sh
        r = int(46 * (1 - t) + 34 * t)
        g = int(52 * (1 - t) + 40 * t)
        b = int(64 * (1 - t) + 52 * t)
        draw.line([(0, y), (sw, y)], fill=(r, g, b, 255))

    # Subtle Aurora glow
    aurora = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    adraw = ImageDraw.Draw(aurora)
    adraw.ellipse([120, 60, 740, 320], fill=(136, 192, 208, 65))
    adraw.ellipse([380, 120, 900, 380], fill=(163, 190, 140, 45))
    aurora = aurora.filter(ImageFilter.GaussianBlur(radius=75))
    img = Image.alpha_composite(img, aurora)

    # Crisp Nordic mountain layers
    draw = ImageDraw.Draw(img)
    draw.polygon([(0, sh), (0, 390), (260, 290), (540, 410), (780, 320), (sw, 400), (sw, sh)], fill=(59, 66, 82, 210))
    draw.polygon([(0, sh), (0, 450), (340, 370), (680, 460), (sw, 390), (sw, sh)], fill=(36, 41, 51, 240))

    img_4k = img.resize((WIDTH, HEIGHT), Image.Resampling.BICUBIC)
    _save_png(img_4k, output_path, "Nordic Arctic")


def write_metadata(folder_path: str, name: str, author: str = "Jarvis OS Team"):
    os.makedirs(folder_path, exist_ok=True)
    meta = {
        "KPlugin": {
            "Authors": [{"Name": author}],
            "Id": name.lower().replace(" ", "-"),
            "License": "GPLv3",
            "Name": name
        }
    }
    with open(os.path.join(folder_path, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print(f"[OK] Wrote metadata.json for {name}")


def main():
    base_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "iso-builder", "config", "includes.chroot", "usr", "share", "wallpapers")
    )

    themes = [
        ("jarvis-zen", "Jarvis Zen", create_zen_wallpaper),
        ("jarvis-cyber", "Jarvis Cyber", create_cyber_wallpaper),
        ("jarvis-cupertino-dark", "Jarvis Cupertino Dark", lambda p: create_cupertino_wallpaper(p, dark=True)),
        ("jarvis-cupertino-light", "Jarvis Cupertino Light", lambda p: create_cupertino_wallpaper(p, dark=False)),
        ("jarvis-nordic", "Jarvis Nordic", create_nordic_wallpaper),
    ]

    for slug, title, gen_fn in themes:
        tdir = os.path.join(base_dir, slug)
        img_path = os.path.join(tdir, "contents", "images", "3840x2160.png")
        gen_fn(img_path)
        write_metadata(tdir, title)


if __name__ == "__main__":
    main()
