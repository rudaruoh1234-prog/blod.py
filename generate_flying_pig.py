#!/usr/bin/env python3
"""Generate a short video of a pig flying through the sky."""

import math
import os
from pathlib import Path

import imageio.v3 as iio
import numpy as np
from PIL import Image, ImageDraw

WIDTH, HEIGHT = 1280, 720
FPS = 24
DURATION_SEC = 6
FRAMES = FPS * DURATION_SEC
OUT_PATH = Path(os.environ.get("OUT_PATH", "/opt/cursor/artifacts/flying_pig.mp4"))


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def sky_color(y: int) -> tuple[int, int, int]:
    t = y / HEIGHT
    top = (135, 206, 250)
    bottom = (176, 224, 230)
    return (
        int(lerp(top[0], bottom[0], t)),
        int(lerp(top[1], bottom[1], t)),
        int(lerp(top[2], bottom[2], t)),
    )


def draw_cloud(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float, alpha: int = 220) -> None:
    fill = (255, 255, 255, alpha)
    blobs = [
        (cx, cy, int(55 * scale)),
        (cx - int(45 * scale), cy + int(8 * scale), int(40 * scale)),
        (cx + int(50 * scale), cy + int(5 * scale), int(48 * scale)),
        (cx + int(15 * scale), cy - int(18 * scale), int(35 * scale)),
    ]
    for x, y, r in blobs:
        draw.ellipse((x - r, y - r, x + r, y + r), fill=fill)


def draw_pig(
    draw: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
    scale: float,
    wing_angle: float,
) -> None:
    s = scale
    body = (255, 182, 193)
    outline = (180, 90, 110)
    snout = (255, 160, 175)

    # Wings (behind body)
    wing_span = int(70 * s)
    wing_h = int(28 * s)
    for side in (-1, 1):
        angle = wing_angle * side
        wx = cx + side * int(55 * s)
        wy = cy - int(10 * s)
        points = [
            (wx, wy),
            (wx + side * wing_span, wy - int(wing_h * math.cos(angle))),
            (wx + side * int(35 * s), wy + int(15 * s)),
        ]
        draw.polygon(points, fill=(255, 255, 255, 200), outline=(200, 200, 210))

    # Body
    bw, bh = int(90 * s), int(70 * s)
    draw.ellipse((cx - bw, cy - bh, cx + bw, cy + bh), fill=body, outline=outline, width=3)

    # Head
    hx, hy = cx + int(55 * s), cy - int(35 * s)
    hr = int(42 * s)
    draw.ellipse((hx - hr, hy - hr, hx + hr, hy + hr), fill=body, outline=outline, width=3)

    # Snout
    sw, sh = int(28 * s), int(22 * s)
    draw.ellipse((hx + int(18 * s) - sw, hy - sh // 2, hx + int(18 * s) + sw, hy + sh), fill=snout, outline=outline, width=2)
    draw.ellipse((hx + int(24 * s) - int(4 * s), hy - int(3 * s), hx + int(24 * s) + int(4 * s), hy + int(5 * s)), fill=(200, 120, 130))
    draw.ellipse((hx + int(32 * s) - int(4 * s), hy - int(3 * s), hx + int(32 * s) + int(4 * s), hy + int(5 * s)), fill=(200, 120, 130))

    # Eyes
    for ex in (hx - int(12 * s), hx + int(8 * s)):
        draw.ellipse((ex - int(7 * s), hy - int(14 * s), ex + int(7 * s), hy), fill=(40, 40, 50))
        draw.ellipse((ex - int(3 * s), hy - int(12 * s), ex - int(1 * s), hy - int(8 * s)), fill=(255, 255, 255))

    # Ears
    for side, ex in ((-1, hx - int(25 * s)), (1, hx + int(5 * s))):
        ear = [
            (ex, hy - int(30 * s)),
            (ex + side * int(18 * s), hy - int(55 * s)),
            (ex + side * int(28 * s), hy - int(20 * s)),
        ]
        draw.polygon(ear, fill=body, outline=outline)

    # Legs (tucked while flying)
    for lx in (cx - int(35 * s), cx - int(10 * s), cx + int(15 * s)):
        draw.line((lx, cy + int(50 * s), lx - int(5 * s), cy + int(75 * s)), fill=outline, width=int(6 * s))

    # Curly tail
    tail_cx, tail_cy = cx - int(75 * s), cy - int(10 * s)
    for i in range(8):
        a = i * 0.9 + 0.3
        tx = tail_cx + int(12 * s * math.cos(a))
        ty = tail_cy + int(12 * s * math.sin(a))
        draw.ellipse((tx - int(6 * s), ty - int(6 * s), tx + int(6 * s), ty + int(6 * s)), fill=body, outline=outline)


def render_frame(frame_idx: int) -> np.ndarray:
    t = frame_idx / FRAMES
    base = Image.new("RGB", (WIDTH, HEIGHT))
    draw_base = ImageDraw.Draw(base)
    for y in range(HEIGHT):
        draw_base.line([(0, y), (WIDTH, y)], fill=sky_color(y))

    # Sun
    sun_x, sun_y = WIDTH - 140, 110
    draw_base.ellipse((sun_x - 55, sun_y - 55, sun_x + 55, sun_y + 55), fill=(255, 236, 139))

    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    cloud_specs = [
        (180, 120, 1.0, 0.0),
        (420, 200, 0.8, 0.15),
        (700, 90, 1.1, 0.3),
        (950, 160, 0.9, 0.45),
        (1100, 280, 0.7, 0.6),
        (300, 380, 1.2, 0.25),
        (850, 420, 1.0, 0.5),
    ]
    for i, (bx, by, sc, phase) in enumerate(cloud_specs):
        offset = int((t * WIDTH * 0.35 + phase * WIDTH) % (WIDTH + 200)) - 100
        draw_cloud(draw, (bx + offset) % (WIDTH + 300) - 150, by, sc)

    # Pig path: gentle arc across screen with bobbing
    progress = t
    pig_x = int(lerp(-120, WIDTH + 120, progress))
    pig_y = int(HEIGHT * 0.42 + math.sin(t * math.pi * 4) * 35 + math.sin(t * math.pi * 2) * 20)
    bob = math.sin(frame_idx / 6) * 0.15
    wing = math.sin(frame_idx / 5) * 0.55 + 0.35

    draw_pig(draw, pig_x, pig_y, 1.15 + bob * 0.05, wing)

    # Sparkles / motion lines
    for i in range(5):
        sx = pig_x - 100 - i * 22
        sy = pig_y + int(math.sin(frame_idx * 0.4 + i) * 8)
        alpha = 120 - i * 20
        draw.line((sx, sy, sx - 18, sy), fill=(255, 255, 255, alpha), width=2)

    composed = Image.alpha_composite(base.convert("RGBA"), layer).convert("RGB")
    return np.array(composed)


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
