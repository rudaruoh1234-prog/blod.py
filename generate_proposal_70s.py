#!/usr/bin/env python3
"""Build a photorealistic 1970s-style proposal clip from stock footage."""

from __future__ import annotations

import os
import subprocess
import sys
import urllib.request
from pathlib import Path

# Mixkit — free for personal use: https://mixkit.co/license/
DEFAULT_SOURCE = "https://assets.mixkit.co/videos/46923/46923-720.mp4"
SOURCE_URL = os.environ.get("SOURCE_URL", DEFAULT_SOURCE)
DURATION = float(os.environ.get("DURATION", "8"))
OUT_PATH = Path(os.environ.get("OUT_PATH", "/opt/cursor/artifacts/proposal_70s.mp4"))
FONT_PATH = os.environ.get(
    "FONT_PATH",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
)
SUBTITLE = os.environ.get("SUBTITLE", "나와 결혼해 주실래요?")


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 100_000:
        return
    print(f"Downloading stock footage from {url} ...")
    urllib.request.urlretrieve(url, dest)


def build_filter(subtitle: str, font: str, duration: float) -> str:
    text_start = max(0.0, duration - 1.6)
    escaped = subtitle.replace("'", r"'\''").replace(":", r"\:")
    return (
        f"eq=contrast=1.12:brightness=0.02:saturation=0.72,"
        f"colorbalance=rs=0.1:gs=0.03:bs=-0.15:rh=0.18:gh=0.1:bh=-0.22,"
        f"curves=r='0/0.06 0.45/0.55 1/0.94':g='0/0.05 0.45/0.52 1/0.9':b='0/0.03 0.45/0.48 1/0.86',"
        f"vignette=angle=PI/4:mode=backward,"
        f"noise=alls=15:allf=t+u,"
        f"drawbox=x=0:y=0:w=iw:h=ih*0.08:color=black@0.55:t=fill,"
        f"drawbox=x=0:y=ih*0.92:w=iw:h=ih*0.08:color=black@0.55:t=fill,"
        f"fade=t=in:st=0:d=0.6,"
        f"drawtext=fontfile={font}:text='{escaped}':fontsize=48:"
        f"fontcolor=#FFE8C8:borderw=2:bordercolor=#2A1810:"
        f"x=(w-text_w)/2:y=h*0.86:enable='between(t\\,{text_start}\\,{duration})'"
    )


def render(source: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    vf = build_filter(SUBTITLE, FONT_PATH, DURATION)
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(source),
        "-t",
        str(DURATION),
        "-vf",
        vf,
        "-an",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-crf",
        "23",
        "-preset",
        "medium",
        "-movflags",
        "+faststart",
        str(dest),
    ]
    print("Running ffmpeg …")
    subprocess.run(cmd, check=True)


def main() -> None:
    cache = Path(os.environ.get("CACHE_DIR", "/tmp/proposal_stock_raw.mp4"))
    if not Path(FONT_PATH).exists():
        print(f"Missing font: {FONT_PATH}", file=sys.stderr)
        print("Install fonts-noto-cjk or set FONT_PATH.", file=sys.stderr)
        sys.exit(1)

    download(SOURCE_URL, cache)
    render(cache, OUT_PATH)
    print(f"Wrote {OUT_PATH} ({DURATION}s, photorealistic stock + 70s grade)")


if __name__ == "__main__":
    main()
