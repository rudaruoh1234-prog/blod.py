#!/usr/bin/env python3
"""Create a ~20s vertical shorts video about collateral loans (담보대출)."""

from __future__ import annotations

import os
import subprocess
import sys
import urllib.request
from pathlib import Path

WIDTH, HEIGHT = 1080, 1920
FPS = 30
SEGMENT_SEC = 4
OUT_PATH = Path(os.environ.get("OUT_PATH", "/opt/cursor/artifacts/collateral_loan_shorts.mp4"))
ASSET_DIR = Path(os.environ.get("ASSET_DIR", "/workspace/assets/collateral"))
FONT_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_REG = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

# Unsplash — free to use under Unsplash License
SLIDES = [
    {
        "id": "intro",
        "url": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&w=1200&q=80",
        "title": "담보대출",
        "subtitle": "토지·건물·상가로\n안전하게 자금을 마련하세요",
        "accent": "#1E4D8C",
    },
    {
        "id": "land",
        "url": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1200&q=80",
        "title": "토지 담보",
        "subtitle": "택지·농지·개발부지 등\n토지를 담보로 대출",
        "accent": "#2D6A4F",
    },
    {
        "id": "building",
        "url": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1200&q=80",
        "title": "건물 담보",
        "subtitle": "아파트·오피스텔·빌딩\n부동산 담보 대출",
        "accent": "#5C4D7D",
    },
    {
        "id": "commercial",
        "url": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=1200&q=80",
        "title": "상가·점포 담보",
        "subtitle": "상가·근린생활시설\n임대수익형 담보",
        "accent": "#B5651D",
    },
    {
        "id": "outro",
        "url": "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?auto=format&fit=crop&w=1200&q=80",
        "title": "담보 가치 평가",
        "subtitle": "감정평가 후\n적정 한도로 대출 실행",
        "accent": "#1E4D8C",
    },
]


def download_assets() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    for slide in SLIDES:
        path = ASSET_DIR / f"{slide['id']}.jpg"
        if path.exists() and path.stat().st_size > 10_000:
            slide["path"] = path
            continue
        print(f"Downloading {slide['id']} …")
        req = urllib.request.Request(slide["url"], headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            path.write_bytes(resp.read())
        slide["path"] = path


def escape_drawtext(text: str) -> str:
    return text.replace("\\", "\\\\").replace("'", "'\\''").replace(":", "\\:").replace("%", "\\%")


def build_segment(slide: dict, index: int, tmp_dir: Path) -> Path:
    frames = FPS * SEGMENT_SEC
    out = tmp_dir / f"seg_{index:02d}.mp4"
    title = escape_drawtext(slide["title"])
    subtitle = escape_drawtext(slide["subtitle"])
    accent = slide["accent"]

    # Ken Burns + gradient overlay + Korean captions
    vf = (
        f"scale={WIDTH * 2}:{HEIGHT * 2}:force_original_aspect_ratio=increase,"
        f"crop={WIDTH * 2}:{HEIGHT * 2},"
        f"zoompan=z='min(1.0+0.0009*on,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d={frames}:s={WIDTH}x{HEIGHT}:fps={FPS},"
        f"eq=brightness=0.06:contrast=1.05:saturation=1.08,"
        f"drawbox=x=0:y=ih*0.68:w=iw:h=ih*0.32:color=black@0.45:t=fill,"
        f"drawbox=x=0:y=ih*0.68:w=iw:h=ih*0.06:color={accent}@1.0:t=fill,"
        f"drawtext=fontfile={FONT_BOLD}:text='{title}':fontsize=76:fontcolor=white:"
        f"borderw=3:bordercolor=black@0.5:x=(w-text_w)/2:y=h*0.70,"
        f"drawtext=fontfile={FONT_REG}:text='{subtitle}':fontsize=44:fontcolor=#FFFFFF:"
        f"borderw=2:bordercolor=black@0.4:line_spacing=14:x=(w-text_w)/2:y=h*0.79,"
        f"fade=t=in:st=0:d=8:alpha=1,fade=t=out:st={frames - 8}:d=8:alpha=1"
    )

    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", str(slide["path"]),
        "-vf", vf, "-t", str(SEGMENT_SEC),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "22", "-preset", "fast",
        str(out),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return out


def concat_segments(segments: list[Path], dest: Path) -> None:
    list_file = segments[0].parent / "concat.txt"
    list_file.write_text("\n".join(f"file '{s}'" for s in segments))
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "22",
        "-movflags", "+faststart", str(dest),
    ]
    subprocess.run(cmd, check=True)


def add_progress_bar(src: Path, dest: Path, total_sec: int) -> None:
    """Subtle progress indicator for shorts feel."""
    vf = (
        f"drawbox=x=40:y=h-28:w=iw-80:h=6:color=white@0.25:t=fill,"
        f"drawbox=x=40:y=h-28:w='(iw-80)*t/{total_sec}':h=6:color=#FFD166@0.9:t=fill"
    )
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(src), "-vf", vf, "-c:v", "libx264", "-crf", "22", "-c:a", "copy", str(dest)],
        check=True,
        capture_output=True,
    )


def main() -> None:
    if not Path(FONT_BOLD).exists():
        print("Install fonts-noto-cjk", file=sys.stderr)
        sys.exit(1)

    tmp = Path("/tmp/collateral_shorts")
    tmp.mkdir(exist_ok=True)

    download_assets()
    segments = [build_segment(slide, i, tmp) for i, slide in enumerate(SLIDES)]
    raw = tmp / "raw.mp4"
    concat_segments(segments, raw)

    total = len(SLIDES) * SEGMENT_SEC
    add_progress_bar(raw, OUT_PATH, total)
    print(f"Wrote {OUT_PATH} ({total}s, {WIDTH}x{HEIGHT} shorts)")


if __name__ == "__main__":
    main()
