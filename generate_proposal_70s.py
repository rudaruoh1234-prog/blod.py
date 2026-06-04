#!/usr/bin/env python3
"""Generate a 1970s-style proposal animation."""

import math
import os
import random
from pathlib import Path

import imageio.v3 as iio
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

WIDTH, HEIGHT = 1280, 720
FPS = 24
DURATION_SEC = 8
FRAMES = FPS * DURATION_SEC
OUT_PATH = Path(os.environ.get("OUT_PATH", "/opt/cursor/artifacts/proposal_70s.mp4"))

# 70s palette
SKY_TOP = (255, 140, 90)
SKY_BOT = (255, 200, 120)
GROUND = (139, 115, 85)
GRASS = (107, 142, 78)
SUN = (255, 220, 100)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def lerp_color(c1: tuple[int, ...], c2: tuple[int, ...], t: float) -> tuple[int, int, int]:
    return (
        int(lerp(c1[0], c2[0], t)),
        int(lerp(c1[1], c2[1], t)),
        int(lerp(c1[2], c2[2], t)),
    )


def draw_sky(base: Image.Image) -> None:
    draw = ImageDraw.Draw(base)
    for y in range(int(HEIGHT * 0.62)):
        t = y / (HEIGHT * 0.62)
        draw.line([(0, y), (WIDTH, y)], fill=lerp_color(SKY_TOP, SKY_BOT, t))
    # Sun with halation
    sx, sy = WIDTH - 200, 130
    for r, alpha in [(90, 40), (70, 80), (50, 180)]:
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.ellipse((sx - r, sy - r, sx + r, sy + r), fill=(*SUN, alpha))
        base.paste(Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB"))


def draw_hills(base: Image.Image) -> None:
    draw = ImageDraw.Draw(base)
    draw.polygon(
        [(0, HEIGHT), (0, 420), (280, 380), (520, 400), (780, 360), (WIDTH, 390), (WIDTH, HEIGHT)],
        fill=GRASS,
    )
    draw.polygon(
        [(0, HEIGHT), (0, 480), (350, 450), (640, 470), (WIDTH, 440), (WIDTH, HEIGHT)],
        fill=GROUND,
    )
    # Retro stripes on ground
    for i in range(0, WIDTH, 80):
        draw.rectangle((i, HEIGHT - 80, i + 40, HEIGHT), fill=(160, 130, 95))


def draw_tree(draw: ImageDraw.ImageDraw, x: int, y: int, scale: float = 1.0) -> None:
    s = scale
    trunk = (101, 67, 33)
    draw.rectangle((x - int(8 * s), y, x + int(8 * s), y + int(70 * s)), fill=trunk)
    draw.ellipse((x - int(45 * s), y - int(55 * s), x + int(45 * s), y + int(15 * s)), fill=(85, 120, 60))
    draw.ellipse((x - int(35 * s), y - int(75 * s), x + int(35 * s), y - int(25 * s)), fill=(95, 135, 70))


def draw_person(
    draw: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
    scale: float,
    is_man: bool,
    pose: str,
    frame: int,
) -> None:
    s = scale
    skin = (255, 213, 170)
    hair = (60, 40, 30) if is_man else (120, 70, 45)
    outfit = (180, 60, 50) if is_man else (220, 100, 140)  # rust / dusty rose
    pants = (70, 90, 130)  # denim
    shoes = (50, 35, 25)

    # Legs
    if pose == "kneel" and is_man:
        # Kneeling silhouette: one knee down, other leg folded back on ground
        thigh_bot = cy + int(42 * s)
        draw.polygon(
            [
                (cx - int(8 * s), cy + int(35 * s)),
                (cx + int(22 * s), thigh_bot),
                (cx + int(38 * s), cy + int(98 * s)),
                (cx + int(12 * s), cy + int(102 * s)),
                (cx - int(5 * s), cy + int(70 * s)),
            ],
            fill=pants,
            outline=(55, 70, 100),
        )
        draw.polygon(
            [
                (cx - int(10 * s), cy + int(35 * s)),
                (cx - int(38 * s), cy + int(72 * s)),
                (cx - int(55 * s), cy + int(98 * s)),
                (cx - int(28 * s), cy + int(102 * s)),
                (cx - int(8 * s), cy + int(68 * s)),
            ],
            fill=pants,
            outline=(55, 70, 100),
        )
        draw.ellipse((cx + int(6 * s), cy + int(94 * s), cx + int(36 * s), cy + int(108 * s)), fill=shoes)
        draw.ellipse((cx - int(58 * s), cy + int(92 * s), cx - int(26 * s), cy + int(106 * s)), fill=shoes)
        torso_y = cy - int(10 * s)
        lean = int(8 * s)
    else:
        leg_sway = int(math.sin(frame / 12) * 3 * s) if pose == "idle" else 0
        draw.line((cx - int(14 * s) + leg_sway, cy + int(40 * s), cx - int(14 * s), cy + int(100 * s)), fill=pants if is_man else (160, 80, 100), width=int(14 * s))
        draw.line((cx + int(14 * s) - leg_sway, cy + int(40 * s), cx + int(14 * s), cy + int(100 * s)), fill=pants if is_man else (160, 80, 100), width=int(14 * s))
        draw.ellipse((cx - int(28 * s), cy + int(92 * s), cx + int(2 * s), cy + int(112 * s)), fill=shoes)
        draw.ellipse((cx + int(2 * s), cy + int(92 * s), cx + int(32 * s), cy + int(112 * s)), fill=shoes)
        torso_y = cy
        lean = 0

    # Torso / 70s wide collar shirt or dress
    bw, bh = int(38 * s), int(55 * s)
    draw.rounded_rectangle(
        (cx - bw + lean, torso_y - bh, cx + bw + lean, torso_y + int(15 * s)),
        radius=int(12 * s),
        fill=outfit,
        outline=(120, 40, 35) if is_man else (160, 70, 100),
        width=2,
    )
    # Collar flare
    if is_man:
        draw.polygon(
            [
                (cx - int(30 * s) + lean, torso_y - int(45 * s)),
                (cx + lean, torso_y - int(25 * s)),
                (cx + int(30 * s) + lean, torso_y - int(45 * s)),
                (cx + lean, torso_y - int(35 * s)),
            ],
            fill=(240, 230, 210),
        )

    # Arms
    if pose == "kneel" and is_man:
        # Offering ring box
        arm_y = torso_y + int(5 * s)
        draw.line((cx + lean, arm_y, cx + int(45 * s), arm_y + int(20 * s)), fill=skin, width=int(10 * s))
        box_x, box_y = cx + int(50 * s), arm_y + int(18 * s)
        open_amt = min(1.0, frame / 40.0)
        draw.rectangle((box_x - int(14 * s), box_y, box_x + int(14 * s), box_y + int(10 * s)), fill=(80, 50, 40))
        draw.polygon(
            [
                (box_x - int(14 * s), box_y),
                (box_x, box_y - int(18 * s * open_amt)),
                (box_x + int(14 * s), box_y),
            ],
            fill=(100, 65, 50),
        )
        if open_amt > 0.3:
            draw.ellipse((box_x - int(5 * s), box_y - int(22 * s), box_x + int(5 * s), box_y - int(12 * s)), fill=(255, 230, 120), outline=(220, 180, 60))
    elif not is_man and pose == "react":
        # Hands to cheeks
        draw.line((cx - int(35 * s), torso_y - int(20 * s), cx - int(50 * s), torso_y - int(45 * s)), fill=skin, width=int(9 * s))
        draw.line((cx + int(35 * s), torso_y - int(20 * s), cx + int(50 * s), torso_y - int(45 * s)), fill=skin, width=int(9 * s))
    else:
        draw.line((cx - int(35 * s), torso_y - int(15 * s), cx - int(48 * s), torso_y + int(15 * s)), fill=skin, width=int(9 * s))
        draw.line((cx + int(35 * s), torso_y - int(15 * s), cx + int(48 * s), torso_y + int(15 * s)), fill=skin, width=int(9 * s))

    # Head
    hy = torso_y - int(58 * s)
    hr = int(28 * s)
    draw.ellipse((cx - hr + lean, hy - hr, cx + hr + lean, hy + hr), fill=skin, outline=(200, 160, 130), width=2)

    # Hair — 70s volume
    if is_man:
        draw.arc((cx - int(32 * s) + lean, hy - int(38 * s), cx + int(32 * s) + lean, hy + int(5 * s)), 200, 340, fill=hair, width=int(12 * s))
        # Mustache
        draw.arc((cx - int(12 * s) + lean, hy + int(2 * s), cx + int(12 * s) + lean, hy + int(14 * s)), 10, 170, fill=hair, width=3)
    else:
        draw.ellipse((cx - int(34 * s), hy - int(42 * s), cx + int(34 * s), hy + int(8 * s)), fill=hair)
        # Farrah-style waves
        for i in range(3):
            draw.arc((cx - int(40 * s) + i * 8, hy - int(20 * s), cx - int(10 * s) + i * 8, hy + int(30 * s)), 90, 220, fill=hair, width=int(6 * s))

    # Face
    eye_y = hy + int(2 * s)
    for ex in (cx - int(10 * s) + lean, cx + int(10 * s) + lean):
        if not is_man and pose == "react" and frame > 50:
            # Happy closed eyes
            draw.arc((ex - int(6 * s), eye_y - int(4 * s), ex + int(6 * s), eye_y + int(6 * s)), 0, 180, fill=(50, 40, 35), width=2)
        else:
            draw.ellipse((ex - int(4 * s), eye_y - int(5 * s), ex + int(4 * s), eye_y + int(5 * s)), fill=(50, 40, 35))

    if not is_man and pose == "react" and frame > 55:
        draw.arc((cx - int(14 * s) + lean, hy + int(12 * s), cx + int(14 * s) + lean, hy + int(24 * s)), 10, 170, fill=(200, 80, 90), width=3)
    elif is_man:
        draw.line((cx - int(8 * s) + lean, hy + int(14 * s), cx + int(8 * s) + lean, hy + int(16 * s)), fill=(180, 100, 90), width=2)


def draw_hearts(draw: ImageDraw.ImageDraw, frame: int, cx: int, cy: int) -> None:
    if frame < 60:
        return
    for i in range(6):
        t = (frame - 60 + i * 8) / 50.0
        if t < 0 or t > 1:
            continue
        hx = cx + int(math.sin(i * 1.7 + frame * 0.08) * 80)
        hy = cy - int(t * 120) - i * 15
        size = int(8 + 6 * (1 - t))
        color = (255, 100, 120, int(200 * (1 - t)))
        draw.ellipse((hx - size, hy - size, hx + size, hy + size), fill=color)
        draw.polygon([(hx, hy + size), (hx - size, hy), (hx + size, hy)], fill=color)


def draw_vintage_overlay(img: Image.Image, frame: int) -> Image.Image:
    rgba = img.convert("RGBA")
    w, h = rgba.size

    # Vignette (radial darkening at edges)
    vig = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    vig_px = vig.load()
    cx, cy = w / 2, h / 2
    max_d = math.hypot(cx, cy)
    for y in range(0, h, 3):
        for x in range(0, w, 3):
            d = math.hypot(x - cx, y - cy) / max_d
            if d > 0.55:
                alpha = int(min(180, (d - 0.55) * 420))
                vig_px[x, y] = (25, 12, 8, alpha)
    vig = vig.filter(ImageFilter.GaussianBlur(radius=18))
    rgba = Image.alpha_composite(rgba, vig)

    # Film grain
    rng = random.Random(frame * 7919)
    grain = Image.new("RGBA", (w, h))
    px = grain.load()
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            n = rng.randint(-28, 28)
            a = rng.randint(8, 35)
            px[x, y] = (n, n, n, a)
    grain = grain.filter(ImageFilter.GaussianBlur(radius=0.6))
    rgba = Image.alpha_composite(rgba, grain)

    # Warm tint
    tint = Image.new("RGBA", (w, h), (255, 180, 100, 35))
    rgba = Image.alpha_composite(rgba, tint)

    # Letterbox bars (cinematic)
    bar = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bar)
    bh = int(h * 0.07)
    bd.rectangle((0, 0, w, bh), fill=(15, 10, 8, 200))
    bd.rectangle((0, h - bh, w, h), fill=(15, 10, 8, 200))
    rgba = Image.alpha_composite(rgba, bar)

    return rgba.convert("RGB")


def draw_title(img: Image.Image, frame: int) -> Image.Image:
    if frame <= FRAMES - 35:
        return img
    alpha = int(255 * min(1.0, (frame - (FRAMES - 35)) / 18.0))
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    text = "Will you marry me?"
    from PIL import ImageFont

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42)
    except OSError:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx = (WIDTH - tw) // 2
    ty = HEIGHT - int(HEIGHT * 0.14) - th
    pad = 24
    draw.rounded_rectangle(
        (tx - pad, ty - pad, tx + tw + pad, ty + th + pad),
        radius=12,
        fill=(30, 20, 15, int(alpha * 0.85)),
    )
    draw.text((tx, ty), text, fill=(255, 220, 180, alpha), font=font)
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def render_frame(frame_idx: int) -> np.ndarray:
    base = Image.new("RGB", (WIDTH, HEIGHT))
    draw_sky(base)
    draw_hills(base)

    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    draw_tree(draw, 180, 320, 1.1)
    draw_tree(draw, 1050, 340, 0.9)
    draw_tree(draw, 90, 380, 0.75)

    man_x, man_y = 480, 380
    woman_x, woman_y = 720, 365

    # Subtle camera push-in
    zoom = 1.0 + frame_idx / FRAMES * 0.04

    man_pose = "kneel"
    woman_pose = "react" if frame_idx > 45 else "idle"

    draw_person(draw, man_x, man_y, 1.0 * zoom, True, man_pose, frame_idx)
    draw_person(draw, woman_x, woman_y, 0.95 * zoom, False, woman_pose, frame_idx)

    draw_hearts(draw, frame_idx, woman_x, woman_y - 80)

    composed = Image.alpha_composite(base.convert("RGBA"), layer).convert("RGB")
    composed = draw_title(composed, frame_idx)
    final = draw_vintage_overlay(composed, frame_idx)
    return np.array(final)


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    frames = [render_frame(i) for i in range(FRAMES)]
    iio.imwrite(
        OUT_PATH,
        frames,
        fps=FPS,
        codec="libx264",
        pixelformat="yuv420p",
        macro_block_size=1,
    )
    print(f"Wrote {OUT_PATH} ({FRAMES} frames, {DURATION_SEC}s)")


if __name__ == "__main__":
    main()
