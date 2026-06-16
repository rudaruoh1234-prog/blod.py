#!/usr/bin/env python3
"""Generate cute dog mascot fortune explanation images."""

from __future__ import annotations

import argparse
import math
import os
import random
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont

from generate_fortune_images import FORTUNE_SETS, FortuneImage, FortuneSet, ensure_font

WIDTH, HEIGHT = 1080, 1080

# Pastel palette
SKY_TOP = (186, 220, 255)
SKY_BOTTOM = (255, 240, 250)
CREAM = (255, 248, 235)
BROWN = (140, 90, 55)
BROWN_DARK = (100, 60, 35)
TAN = (245, 210, 160)
PINK = (255, 180, 190)
PINK_BLUSH = (255, 150, 170)
WHITE = (255, 255, 255)
TEXT_DARK = (55, 45, 65)
TEXT_MID = (90, 80, 105)
ACCENT = (255, 130, 160)
ACCENT_DARK = (230, 90, 130)
BUBBLE = (255, 255, 255)
BUBBLE_BORDER = (255, 200, 215)


def load_font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(ensure_font(), size)


def lerp(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def draw_sky(img: Image.Image) -> None:
    draw = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        t = y / max(HEIGHT - 1, 1)
        draw.line([(0, y), (WIDTH, y)], fill=lerp(SKY_TOP, SKY_BOTTOM, t))


def draw_clouds(draw: ImageDraw.ImageDraw, seed: int) -> None:
    rng = random.Random(seed)
    for _ in range(5):
        cx, cy = rng.randint(60, WIDTH - 60), rng.randint(40, 280)
        for dx, dy, r in [(0, 0, 40), (-35, 8, 28), (35, 8, 28), (-15, -18, 22), (20, -15, 24)]:
            draw.ellipse([cx + dx - r, cy + dy - r, cx + dx + r, cy + dy + r], fill=(255, 255, 255, 180))


def draw_paws(draw: ImageDraw.ImageDraw, seed: int) -> None:
    rng = random.Random(seed + 99)
    for _ in range(6):
        x, y = rng.randint(40, WIDTH - 40), rng.randint(HEIGHT - 200, HEIGHT - 40)
        draw.ellipse([x - 12, y - 10, x + 12, y + 10], fill=(255, 220, 230, 80))
        for ox, oy in [(-8, -12), (8, -12), (-12, 2), (12, 2)]:
            draw.ellipse([x + ox - 5, y + oy - 5, x + ox + 5, y + oy + 5], fill=(255, 220, 230, 70))


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_w: int, draw: ImageDraw.ImageDraw) -> list[str]:
    lines: list[str] = []
    cur = ""
    for ch in text:
        test = cur + ch
        if draw.textbbox((0, 0), test, font=font)[2] <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return lines


def text_size(text: str, font: ImageFont.FreeTypeFont, draw: ImageDraw.ImageDraw) -> tuple[int, int]:
    b = draw.textbbox((0, 0), text, font=font)
    return b[2] - b[0], b[3] - b[1]


def draw_speech_bubble(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    tail: tuple[int, int],
) -> None:
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=36, fill=BUBBLE, outline=BUBBLE_BORDER, width=4)
    tx, ty = tail
    draw.polygon([(tx, ty), (tx + 30, ty - 20), (tx + 55, ty + 10)], fill=BUBBLE, outline=BUBBLE_BORDER)
    draw.line([(tx + 2, ty - 2), (tx + 28, ty - 18)], fill=BUBBLE, width=4)


def draw_cute_dog(
    draw: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
    scale: float = 1.0,
    mood: str = "happy",
    paw_up: bool = False,
) -> None:
    s = scale

    # Body
    draw.ellipse([cx - int(90 * s), cy + int(20 * s), cx + int(90 * s), cy + int(150 * s)], fill=TAN, outline=BROWN, width=3)
    # Belly patch
    draw.ellipse([cx - int(50 * s), cy + int(50 * s), cx + int(50 * s), cy + int(120 * s)], fill=CREAM)

    # Head
    hx, hy = cx, cy - int(30 * s)
    draw.ellipse([hx - int(85 * s), hy - int(75 * s), hx + int(85 * s), hy + int(75 * s)], fill=TAN, outline=BROWN, width=3)

    # Ears
    for side in (-1, 1):
        ex = hx + side * int(70 * s)
        draw.ellipse([ex - int(35 * s), hy - int(90 * s), ex + int(35 * s), hy - int(10 * s)], fill=BROWN)
        draw.ellipse([ex - int(22 * s), hy - int(75 * s), ex + int(22 * s), hy - int(20 * s)], fill=(200, 140, 100))

    # Face patch
    draw.ellipse([hx - int(45 * s), hy - int(20 * s), hx + int(45 * s), hy + int(55 * s)], fill=CREAM)

    # Eyes
    for side in (-1, 1):
        ex = hx + side * int(32 * s)
        ey = hy - int(8 * s)
        draw.ellipse([ex - int(16 * s), ey - int(18 * s), ex + int(16 * s), ey + int(18 * s)], fill=WHITE, outline=BROWN, width=2)
        draw.ellipse([ex - int(9 * s), ey - int(10 * s), ex + int(9 * s), ey + int(10 * s)], fill=(30, 30, 40))
        draw.ellipse([ex - int(4 * s), ey - int(8 * s), ex - int(1 * s), ey - int(5 * s)], fill=WHITE)

    # Blush
    for side in (-1, 1):
        bx = hx + side * int(55 * s)
        draw.ellipse([bx - int(14 * s), hy + int(12 * s), bx + int(14 * s), hy + int(28 * s)], fill=(255, 170, 185))

    # Nose
    draw.ellipse([hx - int(12 * s), hy + int(10 * s), hx + int(12 * s), hy + int(24 * s)], fill=BROWN_DARK)

    # Mouth
    if mood == "happy":
        draw.arc([hx - int(22 * s), hy + int(18 * s), hx + int(22 * s), hy + int(42 * s)], 20, 160, fill=BROWN_DARK, width=3)
        draw.ellipse([hx - int(5 * s), hy + int(30 * s), hx + int(5 * s), hy + int(38 * s)], fill=(255, 120, 140))
    elif mood == "explain":
        draw.ellipse([hx - int(14 * s), hy + int(28 * s), hx + int(14 * s), hy + int(44 * s)], fill=(255, 100, 120), outline=BROWN_DARK, width=2)
    elif mood == "think":
        draw.arc([hx - int(18 * s), hy + int(26 * s), hx + int(10 * s), hy + int(44 * s)], 200, 320, fill=BROWN_DARK, width=3)
    else:  # excited
        draw.ellipse([hx - int(16 * s), hy + int(26 * s), hx + int(16 * s), hy + int(46 * s)], fill=(255, 100, 120), outline=BROWN_DARK, width=2)

    # Bandana
    draw.polygon(
        [
            (hx - int(50 * s), hy + int(45 * s)),
            (hx + int(50 * s), hy + int(45 * s)),
            (hx + int(60 * s), hy + int(80 * s)),
            (hx, hy + int(95 * s)),
            (hx - int(60 * s), hy + int(80 * s)),
        ],
        fill=ACCENT,
        outline=ACCENT_DARK,
    )
    draw.ellipse([hx - int(8 * s), hy + int(72 * s), hx + int(8 * s), hy + int(88 * s)], fill=ACCENT_DARK)

    # Paws
    if paw_up:
        px, py = cx + int(75 * s), cy + int(10 * s)
        draw.ellipse([px - int(28 * s), py - int(22 * s), px + int(28 * s), py + int(22 * s)], fill=TAN, outline=BROWN, width=2)
        for ox, oy in [(-10, -14), (10, -14), (-14, 2), (14, 2)]:
            draw.ellipse([px + ox - 6, py + oy - 6, px + ox + 6, py + oy + 6], fill=CREAM)
    for side, lift in [(-1, 0), (1, 0)]:
        px = cx + side * int(55 * s)
        py = cy + int(130 * s) - lift
        draw.ellipse([px - int(24 * s), py - int(18 * s), px + int(24 * s), py + int(18 * s)], fill=TAN, outline=BROWN, width=2)

    # Tail
    draw.arc([cx + int(60 * s), cy + int(30 * s), cx + int(130 * s), cy + int(110 * s)], 280, 60, fill=BROWN, width=int(12 * s))


MOOD_MAP = {
    "representative": ("happy", True),
    "rising": ("explain", True),
    "dragon": ("excited", True),
    "handshake": ("happy", True),
    "scale": ("think", False),
    "number": ("excited", True),
    "piggy": ("think", False),
    "envelope": ("excited", True),
    "horizon": ("happy", False),
}


def dog_speech(spec: FortuneImage) -> str:
    if spec.index is None:
        return (
            f"멍멍! 나 뭉치야~ 오늘 {spec.title}!\n"
            f"핵심은 「{spec.phrase}」야!\n"
            f"{spec.caption} ✨"
        )
    return (
        f"【{spec.title}】\n"
        f"「{spec.phrase}」\n"
        f"{spec.caption}"
    )


def create_dog_image(spec: FortuneImage, fortune_set: FortuneSet) -> Image.Image:
    img = Image.new("RGBA", (WIDTH, HEIGHT), SKY_TOP)
    draw_sky(img)
    draw = ImageDraw.Draw(img, "RGBA")
    seed = (spec.index or 0) * 77 + 3
    draw_clouds(draw, seed)
    draw_paws(draw, seed)

    # Header ribbon
    draw.rounded_rectangle([60, 40, WIDTH - 60, 110], radius=28, fill=ACCENT, outline=ACCENT_DARK, width=3)
    header_font = load_font(36 if spec.index is None else 32)
    header = spec.title if spec.index is None else f"🐾 {spec.title}"
    hw, hh = text_size(header, header_font, draw)
    draw.text(((WIDTH - hw) // 2, 62), header, font=header_font, fill=WHITE)

    # Speech bubble
    bubble_box = (120, 150, WIDTH - 80, 620)
    draw_speech_bubble(draw, bubble_box, tail=(200, 640))

    speech = dog_speech(spec)
    speech_font = load_font(34)
    phrase_font = load_font(48 if len(spec.phrase) <= 6 else 40)

    y = 200
    lines = speech.split("\n")
    for i, line in enumerate(lines):
        font = phrase_font if i == 1 or (spec.index is None and i == 1) else speech_font
        color = ACCENT_DARK if (i == 1 or (spec.index is None and "핵심" in line)) else TEXT_DARK
        if "「" in line:
            font = phrase_font
            color = ACCENT_DARK
        wrapped = wrap_text(line, font, bubble_box[2] - bubble_box[0] - 60, draw)
        for wl in wrapped:
            w, h = text_size(wl, font, draw)
            draw.text((bubble_box[0] + 40, y), wl, font=font, fill=color)
            y += h + 14

    # Phrase highlight badge
    badge_font = load_font(30)
    badge_text = f"💛 {spec.phrase}"
    bw, bh = text_size(badge_text, badge_font, draw)
    bx = (WIDTH - bw) // 2
    by = 640
    draw.rounded_rectangle([bx - 20, by - 10, bx + bw + 20, by + bh + 14], radius=20, fill=(255, 230, 180), outline=(255, 190, 120), width=2)
    draw.text((bx, by), badge_text, font=badge_font, fill=BROWN_DARK)

    mood, paw_up = MOOD_MAP.get(spec.icon, ("happy", True))
    draw_cute_dog(draw, cx=280, cy=HEIGHT - 280, scale=1.15, mood=mood, paw_up=paw_up)

    # Footer
    footer_font = load_font(26)
    footer = f"🐶 뭉치가 알려주는 운세  ·  {fortune_set.date_label}"
    fw, _ = text_size(footer, footer_font, draw)
    draw.text(((WIDTH - fw) // 2, HEIGHT - 55), footer, font=footer_font, fill=TEXT_MID)

    return img.convert("RGB")


def generate_dog_set(date_key: str) -> str:
    fortune_set = FORTUNE_SETS[date_key]
    output_dir = os.path.join(os.path.dirname(__file__), "images", date_key, "dog")
    os.makedirs(output_dir, exist_ok=True)
    for spec in fortune_set.images:
        img = create_dog_image(spec, fortune_set)
        path = os.path.join(output_dir, spec.filename)
        img.save(path, "PNG", optimize=True)
        print(f"Created: {path}")
    print(f"\nDone! {len(fortune_set.images)} dog images -> {output_dir}")
    return output_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate cute dog fortune images.")
    parser.add_argument("--date", default="2025-06-18", choices=sorted(FORTUNE_SETS.keys()))
    args = parser.parse_args()
    ensure_font()
    generate_dog_set(args.date)


if __name__ == "__main__":
    main()
