#!/usr/bin/env python3
"""Create a ~30s vertical shorts video about commercial property loans (상가대출)."""

from __future__ import annotations

import asyncio
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

import edge_tts

WIDTH, HEIGHT = 1080, 1920
FPS = 30
SEGMENT_SEC = 5
TITLE_SIZE = 96
SUBTITLE_SIZE = 58
HEADER_H = 178
OUT_PATH = Path(os.environ.get("OUT_PATH", "/opt/cursor/artifacts/commercial_loan_shorts.mp4"))
ASSET_DIR = Path(os.environ.get("ASSET_DIR", "/workspace/assets/commercial"))
FONT_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_REG = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
CONTACT_NAME = os.environ.get("CONTACT_NAME", "이차장")
CONTACT_PHONE = os.environ.get("CONTACT_PHONE", "010-6704-1290")
TTS_VOICE = os.environ.get("TTS_VOICE", "ko-KR-InJoonNeural")
TTS_RATE = os.environ.get("TTS_RATE", "-12%")
TTS_PITCH = os.environ.get("TTS_PITCH", "-4Hz")

SLIDES = [
    {
        "id": "intro",
        "url": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?auto=format&fit=crop&w=1400&q=85",
        "title": "상가대출",
        "subtitle": "층수·연면적·입지를 반영한\n상가 맞춤 자금 솔루션",
        "narration": "상가대출은 층수와 연면적, 입지를 반영해 맞춤 자금을 설계하는 대출입니다.",
        "accent": "#C45C26",
    },
    {
        "id": "floors",
        "url": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1400&q=85",
        "title": "층별·전체 높이 평가",
        "subtitle": "지상층·지하층·옥탑 권리까지\n건물 전체 높이를 담보로 산정",
        "narration": "지상층, 지하층, 옥탑 권리까지 건물 전체 높이를 기준으로 담보 가치를 산정합니다.",
        "accent": "#1E4D8C",
    },
    {
        "id": "rent",
        "url": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=1400&q=85",
        "title": "임대수익형 담보",
        "subtitle": "월세·권리금·환산보증금\n공실률까지 반영한 상환 설계",
        "narration": "월세, 권리금, 환산보증금과 공실률까지 반영해 안정적인 상환 계획을 세웁니다.",
        "accent": "#2D6A4F",
    },
    {
        "id": "types",
        "url": "https://images.unsplash.com/photo-1577415124269-fc1140a69e91?auto=format&fit=crop&w=1400&q=85",
        "title": "근린·집합·복층 상가",
        "subtitle": "1층 점포부터 복층 매장까지\n업종·유동인구·층고 검토",
        "narration": "근린상가, 집합상가, 복층 매장까지 업종과 유동인구, 층고를 꼼꼼히 검토합니다.",
        "accent": "#6B3FA0",
    },
    {
        "id": "ltv",
        "url": "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?auto=format&fit=crop&w=1400&q=85",
        "title": "감정평가·LTV",
        "subtitle": "전문 감정 후 담보 인정비율\n합리적 대출 한도·금리 제안",
        "narration": "전문 감정평가 후 담보 인정 비율에 따라 합리적인 대출 한도와 금리를 제안드립니다.",
        "accent": "#1E4D8C",
    },
    {
        "id": "cta",
        "url": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&w=1400&q=85",
        "title": "상가대출 상담",
        "subtitle": "서류·한도·실행 일정\n빠르게 안내해 드립니다",
        "narration": "서류, 한도, 실행 일정을 빠르게 안내해 드립니다. 화면 상단 연락처로 편하게 문의해 주세요.",
        "accent": "#C45C26",
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


async def synthesize_narration(slide: dict, audio_path: Path) -> None:
    communicate = edge_tts.Communicate(
        slide["narration"],
        TTS_VOICE,
        rate=TTS_RATE,
        pitch=TTS_PITCH,
    )
    await communicate.save(str(audio_path))


def fit_audio_to_segment(src: Path, dest: Path) -> None:
    """Trim or slightly speed up narration to fit each 5s segment."""
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(src),
            "-af", "apad=pad_dur=0.2",
            "-t", str(SEGMENT_SEC),
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
            str(dest),
        ],
        check=True,
        capture_output=True,
    )


def build_segment_video(slide: dict, index: int, tmp_dir: Path) -> Path:
    frames = FPS * SEGMENT_SEC
    out = tmp_dir / f"seg_{index:02d}_video.mp4"
    title = escape_drawtext(slide["title"])
    subtitle = escape_drawtext(slide["subtitle"])
    accent = slide["accent"]
    panel_top = 0.58
    title_y = 0.60
    subtitle_y = 0.72

    vf = (
        f"scale={WIDTH * 2}:{HEIGHT * 2}:force_original_aspect_ratio=increase,"
        f"crop={WIDTH * 2}:{HEIGHT * 2},"
        f"zoompan=z='min(1.0+0.00075*on,1.14)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d={frames}:s={WIDTH}x{HEIGHT}:fps={FPS},"
        f"eq=brightness=0.07:contrast=1.08:saturation=1.1,"
        f"drawbox=x=0:y=ih*{panel_top}:w=iw:h=ih*{1 - panel_top}:color=black@0.5:t=fill,"
        f"drawbox=x=0:y=ih*{panel_top}:w=iw:h=ih*0.07:color={accent}@1.0:t=fill,"
        f"drawtext=fontfile={FONT_BOLD}:text='{title}':fontsize={TITLE_SIZE}:fontcolor=white:"
        f"borderw=4:bordercolor=black@0.55:x=(w-text_w)/2:y=h*{title_y},"
        f"drawtext=fontfile={FONT_REG}:text='{subtitle}':fontsize={SUBTITLE_SIZE}:fontcolor=#FFFFFF:"
        f"borderw=3:bordercolor=black@0.45:line_spacing=18:x=(w-text_w)/2:y=h*{subtitle_y},"
        f"fade=t=in:st=0:d=10:alpha=1,fade=t=out:st={frames - 10}:d=10:alpha=1"
    )

    subprocess.run(
        [
            "ffmpeg", "-y", "-loop", "1", "-i", str(slide["path"]),
            "-vf", vf, "-t", str(SEGMENT_SEC),
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "21", "-preset", "fast",
            str(out),
        ],
        check=True,
        capture_output=True,
    )
    return out


def mux_segment(video: Path, audio: Path, out: Path) -> None:
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(video), "-i", str(audio),
            "-c:v", "copy", "-c:a", "aac", "-shortest",
            str(out),
        ],
        check=True,
        capture_output=True,
    )


def concat_segments(segments: list[Path], dest: Path) -> None:
    list_file = segments[0].parent / "concat.txt"
    list_file.write_text("\n".join(f"file '{s}'" for s in segments))
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
            "-c:v", "libx264", "-c:a", "aac", "-pix_fmt", "yuv420p", "-crf", "21",
            "-movflags", "+faststart", str(dest),
        ],
        check=True,
    )


def add_header_and_progress(src: Path, dest: Path, total_sec: int) -> None:
    """Contact header at top + progress bar at bottom."""
    name = escape_drawtext(CONTACT_NAME)
    phone = escape_drawtext(CONTACT_PHONE)
    label = escape_drawtext("상가대출 전문 상담")
    hh = HEADER_H
    vf = (
        f"drawbox=x=0:y=0:w=iw:h={hh}:color=#0B1528@0.94:t=fill,"
        f"drawbox=x=0:y={hh - 6}:w=iw:h=6:color=#FFBE3D@1.0:t=fill,"
        f"drawtext=fontfile={FONT_REG}:text='{label}':fontsize=34:fontcolor=#A8C4FF:"
        f"x=(w-text_w)/2:y=14,"
        f"drawtext=fontfile={FONT_BOLD}:text='{name}':fontsize=58:fontcolor=#FFBE3D:"
        f"borderw=3:bordercolor=black@0.6:x=(w-text_w)/2:y=52,"
        f"drawtext=fontfile={FONT_BOLD}:text='{phone}':fontsize=72:fontcolor=white:"
        f"borderw=4:bordercolor=black@0.65:x=(w-text_w)/2:y=112,"
        f"drawbox=x=36:y=h-24:w=iw-72:h=8:color=white@0.3:t=fill,"
        f"drawbox=x=36:y=h-24:w='(iw-72)*t/{total_sec}':h=8:color=#FFBE3D@1.0:t=fill"
    )
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(src), "-vf", vf,
            "-c:v", "libx264", "-c:a", "aac", "-crf", "21", "-b:a", "192k",
            str(dest),
        ],
        check=True,
        capture_output=True,
    )


async def generate_all_narration(tmp: Path) -> list[Path]:
    tasks = []
    paths = []
    for slide in SLIDES:
        raw = tmp / f"{slide['id']}_voice.mp3"
        fitted = tmp / f"{slide['id']}_voice.aac"
        paths.append(fitted)
        tasks.append((slide, raw, fitted))

    await asyncio.gather(*[synthesize_narration(s, r) for s, r, _ in tasks])
    for _, raw, fitted in tasks:
        fit_audio_to_segment(raw, fitted)
    return paths


def main() -> None:
    if not Path(FONT_BOLD).exists():
        print("Install fonts-noto-cjk", file=sys.stderr)
        sys.exit(1)

    tmp = Path("/tmp/commercial_loan_shorts")
    tmp.mkdir(exist_ok=True)

    download_assets()
    print("Synthesizing narration (male voice) …")
    asyncio.run(generate_all_narration(tmp))

    segments: list[Path] = []
    for i, slide in enumerate(SLIDES):
        video = build_segment_video(slide, i, tmp)
        seg_out = tmp / f"seg_{i:02d}.mp4"
        mux_segment(video, tmp / f"{slide['id']}_voice.aac", seg_out)
        segments.append(seg_out)

    raw = tmp / "raw.mp4"
    concat_segments(segments, raw)

    total = len(SLIDES) * SEGMENT_SEC
    add_header_and_progress(raw, OUT_PATH, total)
    print(f"Wrote {OUT_PATH} ({total}s, {WIDTH}x{HEIGHT}, with narration)")


if __name__ == "__main__":
    main()
