#!/usr/bin/env python3
"""Generate luxury fortune horoscope social media card images."""

from __future__ import annotations

import argparse
import math
import os
import random
from dataclasses import dataclass, field
from typing import Callable

from PIL import Image, ImageDraw, ImageFont

FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts", "NotoSansKR.ttf")
WIDTH, HEIGHT = 1080, 1080
FONT_URL = (
    "https://github.com/google/fonts/raw/main/ofl/notosanskr/"
    "NotoSansKR%5Bwght%5D.ttf"
)

GOLD_LIGHT = (255, 228, 140)
GOLD_MID = (212, 175, 55)
GOLD_DARK = (160, 118, 28)
GOLD_SHADOW = (70, 48, 8)
NAVY_TOP = (10, 20, 52)
NAVY_BOTTOM = (4, 10, 30)
WHITE = (245, 245, 250)
WHITE_DIM = (200, 205, 220)


def ensure_font() -> str:
    if os.path.isfile(FONT_PATH):
        return FONT_PATH
    os.makedirs(os.path.dirname(FONT_PATH), exist_ok=True)
    import urllib.request

    urllib.request.urlretrieve(FONT_URL, FONT_PATH)
    return FONT_PATH


def load_font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(ensure_font(), size)


@dataclass
class FortuneImage:
    filename: str
    title: str
    phrase: str
    caption: str
    icon: str
    index: int | None = None
    laurel: bool = False


@dataclass
class FortuneSet:
    date_label: str
    images: list[FortuneImage] = field(default_factory=list)

    @property
    def slide_count(self) -> int:
        return sum(1 for img in self.images if img.index is not None)


FORTUNE_SETS: dict[str, FortuneSet] = {
    "2025-06-10": FortuneSet(
        date_label="2025. 06. 10",
        images=[
            FortuneImage("00_representative.png", "6월 10일 오늘의 운세", "돈 들어올 가능성", "오늘 재물운이 강한 띠는 누구일까요", "representative", laurel=True),
            FortuneImage("01_today_fortune.png", "오늘 운세", "핵심 요약", "재물운과 귀인운 흐름 분석", "rising", index=1),
            FortuneImage("02_wealth_rank.png", "재물운 순위", "용띠 1위", "금전운 강한 띠 공개", "dragon", index=2),
            FortuneImage("03_case_study.png", "실제 사례", "환급금 확인", "예상 밖 입금 가능성", "envelope", index=3),
            FortuneImage("04_good_contact.png", "좋은 연락", "기회 발생", "새로운 수입 연결 가능", "envelope", index=4),
            FortuneImage("05_career.png", "직장운", "성과 인정", "좋은 평가 기대", "rising", index=5),
            FortuneImage("06_benefactor.png", "귀인운", "도움 도착", "인연이 기회를 만듭니다", "handshake", index=6),
            FortuneImage("07_caution.png", "주의사항", "소비 점검", "충동 지출 주의", "scale", index=7),
            FortuneImage("08_lucky_point.png", "행운 포인트", "8", "오늘의 행운 요소", "number", index=8),
            FortuneImage("09_usage.png", "활용 방법", "참고 활용", "운세를 현명하게 보는 법", "horizon", index=9),
            FortuneImage("10_summary.png", "최종 정리", "재물운 상승", "오늘의 핵심 운세 총정리", "horizon", index=10, laurel=True),
        ],
    ),
    "2025-06-18": FortuneSet(
        date_label="2025. 06. 18",
        images=[
            FortuneImage("00_representative.png", "6월 18일 운세", "재물운 상승", "귀인운과 재물운이 함께 움직이는 하루", "representative", laurel=True),
            FortuneImage("01_today_overview.png", "오늘 총운", "상승 흐름", "오후로 갈수록 운세가 좋아지는 날", "rising", index=1),
            FortuneImage("02_wealth.png", "재물운", "용띠 강세", "금전 기회가 확대될 가능성", "dragon", index=2),
            FortuneImage("03_benefactor.png", "귀인운", "인맥 활용", "좋은 사람을 통해 기회가 찾아옵니다", "handshake", index=3),
            FortuneImage("04_caution.png", "주의 띠", "신중 판단", "충동적인 선택은 피하는 것이 좋습니다", "scale", index=4),
            FortuneImage("05_lucky_element.png", "행운 요소", "8", "오늘의 행운 포인트", "number", index=5),
            FortuneImage("06_money_management.png", "재물 관리", "지출 점검", "불필요한 소비를 줄이는 것이 중요", "piggy", index=6),
            FortuneImage("07_opportunity.png", "기회 포착", "연락 확인", "예상 밖 좋은 소식 가능성", "envelope", index=7),
            FortuneImage("08_summary.png", "최종 정리", "운의 흐름", "재물운과 귀인운을 함께 활용하는 하루", "horizon", index=8),
        ],
    ),
}


def lerp_color(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def draw_vertical_gradient(img: Image.Image, top: tuple[int, int, int], bottom: tuple[int, int, int]) -> None:
    draw = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        t = y / max(HEIGHT - 1, 1)
        draw.line([(0, y), (WIDTH, y)], fill=lerp_color(top, bottom, t))


def draw_constellation(draw: ImageDraw.ImageDraw, seed: int) -> None:
    rng = random.Random(seed)
    stars = [(rng.randint(30, WIDTH - 30), rng.randint(30, HEIGHT - 30)) for _ in range(28)]
    for x, y in stars:
        r = rng.choice([1, 2])
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, rng.randint(30, 90)))
    for _ in range(6):
        a, b = rng.sample(stars, 2)
        draw.line([a, b], fill=(255, 255, 255, 25), width=1)

    cx, cy, r = WIDTH // 2, HEIGHT // 2 + 40, 280
    for deg in range(0, 360, 30):
        rad = math.radians(deg)
        x2 = cx + r * math.cos(rad)
        y2 = cy + r * math.sin(rad)
        draw.line([(cx, cy), (x2, y2)], fill=(GOLD_MID[0], GOLD_MID[1], GOLD_MID[2], 18), width=1)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(GOLD_MID[0], GOLD_MID[1], GOLD_MID[2], 22), width=1)


def draw_mountains(draw: ImageDraw.ImageDraw) -> None:
    base_y = HEIGHT - 120
    peaks = [(0, base_y), (180, base_y - 90), (320, base_y - 40), (500, base_y - 110), (700, base_y - 50), (900, base_y - 100), (WIDTH, base_y - 30), (WIDTH, HEIGHT), (0, HEIGHT)]
    draw.polygon(peaks, fill=(8, 16, 38, 120))


def draw_ornate_frame(draw: ImageDraw.ImageDraw) -> None:
    m = 28
    outer = [m, m, WIDTH - m, HEIGHT - m]
    inner = [m + 14, m + 14, WIDTH - m - 14, HEIGHT - m - 14]
    draw.rounded_rectangle(outer, radius=8, outline=GOLD_MID, width=3)
    draw.rounded_rectangle(inner, radius=6, outline=GOLD_LIGHT, width=1)

    corners = [
        (m + 8, m + 8),
        (WIDTH - m - 8, m + 8),
        (m + 8, HEIGHT - m - 8),
        (WIDTH - m - 8, HEIGHT - m - 8),
    ]
    for cx, cy in corners:
        draw.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], outline=GOLD_LIGHT, width=2)
        draw.line([(cx - 16, cy), (cx + 16, cy)], fill=GOLD_MID, width=2)
        draw.line([(cx, cy - 16), (cx, cy + 16)], fill=GOLD_MID, width=2)


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> list[str]:
    lines: list[str] = []
    current = ""
    for ch in text:
        test = current + ch
        if draw.textbbox((0, 0), test, font=font)[2] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = ch
    if current:
        lines.append(current)
    return lines


def text_size(text: str, font: ImageFont.FreeTypeFont, draw: ImageDraw.ImageDraw) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def draw_gold_text(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    text: str,
    font: ImageFont.FreeTypeFont,
) -> None:
    layers = [
        (5, 6, GOLD_SHADOW),
        (3, 4, GOLD_DARK),
        (1, 2, GOLD_MID),
        (0, 0, GOLD_LIGHT),
    ]
    for ox, oy, color in layers:
        draw.text((x + ox, y + oy), text, font=font, fill=color)


def draw_centered_gold_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    center_y: int,
    font: ImageFont.FreeTypeFont,
    max_width: int = WIDTH - 180,
) -> int:
    lines = wrap_text(text, font, max_width, draw)
    if not lines:
        return center_y
    heights = [text_size(line, font, draw)[1] for line in lines]
    total_h = sum(heights) + 8 * (len(lines) - 1)
    y = center_y - total_h // 2
    for line, h in zip(lines, heights):
        w, _ = text_size(line, font, draw)
        draw_gold_text(draw, (WIDTH - w) // 2, y, line, font)
        y += h + 8
    return y


def draw_centered_white_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    y: int,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int] = WHITE,
    max_width: int = WIDTH - 160,
    spacing: int = 10,
) -> int:
    lines = wrap_text(text, font, max_width, draw)
    for line in lines:
        w, h = text_size(line, font, draw)
        draw.text(((WIDTH - w) // 2, y), line, font=font, fill=fill)
        y += h + spacing
    return y


def draw_laurel_banner(draw: ImageDraw.ImageDraw, cx: int, cy: int, text: str, font: ImageFont.FreeTypeFont) -> None:
    tw, th = text_size(text, font, draw)
    pad_x, pad_y = 50, 22
    left, top = cx - tw // 2 - pad_x, cy - th // 2 - pad_y
    right, bottom = cx + tw // 2 + pad_x, cy + th // 2 + pad_y
    draw.rounded_rectangle([left, top, right, bottom], radius=18, fill=(20, 30, 65, 180), outline=GOLD_MID, width=2)
    for side in (-1, 1):
        bx = left - 8 if side < 0 else right + 8
        draw.arc([bx - 28, cy - 40, bx + 28, cy + 40], 200 if side < 0 else 340, 340 if side < 0 else 200, fill=GOLD_LIGHT, width=3)
    draw_gold_text(draw, cx - tw // 2, cy - th // 2, text, font)


def gold_coin(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int) -> None:
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD_DARK, outline=GOLD_LIGHT, width=2)
    draw.ellipse([cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4], outline=GOLD_LIGHT, width=1)
    inner_font = load_font(max(14, r))
    label = "₩"
    lw, lh = text_size(label, inner_font, draw)
    draw.text((cx - lw // 2, cy - lh // 2 - 2), label, font=inner_font, fill=GOLD_SHADOW)


def icon_rising(draw: ImageDraw.ImageDraw, ox: int, oy: int) -> None:
    for i, (dx, dy, rot) in enumerate([(0, 0, -15), (40, -20, 10), (-35, 15, -25)]):
        x, y = ox + dx, oy + dy
        draw.rounded_rectangle([x, y, x + 70, y + 38], radius=6, fill=GOLD_MID, outline=GOLD_LIGHT, width=1)
        draw.text((x + 18, y + 6), "₩", font=load_font(22), fill=GOLD_SHADOW)
    ax, ay = ox + 20, oy + 70
    draw.polygon([(ax, ay + 50), (ax + 55, ay), (ax + 110, ay + 50)], fill=GOLD_DARK, outline=GOLD_LIGHT)
    draw.polygon([(ax + 55, ay - 5), (ax + 70, ay + 20), (ax + 40, ay + 20)], fill=GOLD_LIGHT)


def icon_dragon(draw: ImageDraw.ImageDraw, ox: int, oy: int) -> None:
    body = [(ox, oy + 50), (ox + 30, oy + 20), (ox + 70, oy + 15), (ox + 110, oy + 35), (ox + 130, oy + 60), (ox + 95, oy + 75), (ox + 50, oy + 70)]
    draw.polygon(body, fill=GOLD_MID, outline=GOLD_LIGHT, width=2)
    draw.ellipse([ox - 8, oy + 38, ox + 22, oy + 62], fill=GOLD_LIGHT, outline=GOLD_DARK)
    draw.polygon([(ox + 125, oy + 45), (ox + 150, oy + 35), (ox + 140, oy + 58)], fill=GOLD_LIGHT)
    for i, cx in enumerate([ox + 145, ox + 160, ox + 175]):
        gold_coin(draw, cx, oy + 95 - i * 8, 16 - i * 2)
    draw.line([(ox + 170, oy + 70), (ox + 170, oy + 35)], fill=GOLD_LIGHT, width=3)
    draw.polygon([(ox + 170, oy + 30), (ox + 185, oy + 45), (ox + 155, oy + 45)], fill=GOLD_LIGHT)


def icon_handshake(draw: ImageDraw.ImageDraw, ox: int, oy: int) -> None:
    draw.rounded_rectangle([ox + 10, oy + 55, ox + 55, oy + 95], radius=8, fill=GOLD_MID, outline=GOLD_LIGHT, width=2)
    draw.rounded_rectangle([ox + 55, oy + 55, ox + 100, oy + 95], radius=8, fill=GOLD_LIGHT, outline=GOLD_DARK, width=2)
    draw.arc([ox + 35, oy + 20, ox + 75, oy + 70], 200, 340, fill=GOLD_LIGHT, width=8)
    draw.arc([ox + 55, oy + 20, ox + 95, oy + 70], 200, 340, fill=GOLD_MID, width=8)


def icon_scale(draw: ImageDraw.ImageDraw, ox: int, oy: int) -> None:
    draw.line([(ox + 70, oy + 20), (ox + 70, oy + 100)], fill=GOLD_LIGHT, width=4)
    draw.line([(ox + 30, oy + 35), (ox + 110, oy + 35)], fill=GOLD_LIGHT, width=4)
    for side, sx in enumerate([ox + 20, ox + 85]):
        draw.line([(sx, oy + 35), (sx + 25, oy + 70)], fill=GOLD_MID, width=3)
        draw.ellipse([sx, oy + 68, sx + 50, oy + 95], outline=GOLD_LIGHT, width=3)
    draw.polygon([(ox + 55, oy + 100), (ox + 85, oy + 100), (ox + 70, oy + 115)], fill=GOLD_MID)


def icon_piggy(draw: ImageDraw.ImageDraw, ox: int, oy: int) -> None:
    draw.ellipse([ox + 20, oy + 35, ox + 100, oy + 95], fill=GOLD_MID, outline=GOLD_LIGHT, width=3)
    draw.ellipse([ox + 88, oy + 52, ox + 108, oy + 72], fill=GOLD_LIGHT, outline=GOLD_DARK)
    draw.ellipse([ox + 42, oy + 58, ox + 52, oy + 68], fill=GOLD_SHADOW)
    draw.ellipse([ox + 62, oy + 58, ox + 72, oy + 68], fill=GOLD_SHADOW)
    draw.polygon([(ox + 95, oy + 45), (ox + 115, oy + 35), (ox + 105, oy + 55)], fill=GOLD_LIGHT)
    # shield
    draw.polygon([(ox + 5, oy + 45), (ox + 25, oy + 30), (ox + 25, oy + 85), (ox + 5, oy + 100)], fill=GOLD_DARK, outline=GOLD_LIGHT, width=2)


def icon_envelope(draw: ImageDraw.ImageDraw, ox: int, oy: int) -> None:
    draw.rounded_rectangle([ox + 15, oy + 35, ox + 115, oy + 100], radius=8, fill=GOLD_MID, outline=GOLD_LIGHT, width=3)
    draw.polygon([(ox + 15, oy + 35), (ox + 65, oy + 72), (ox + 115, oy + 35)], fill=GOLD_LIGHT)
    draw.ellipse([ox + 95, oy + 20, ox + 125, oy + 50], fill=(220, 50, 50), outline=WHITE, width=2)
    draw.text((ox + 104, oy + 24), "!", font=load_font(20), fill=WHITE)


def icon_horizon(draw: ImageDraw.ImageDraw, ox: int, oy: int) -> None:
    draw.polygon([(ox, oy + 95), (ox + 40, oy + 70), (ox + 80, oy + 82), (ox + 130, oy + 55), (ox + 130, oy + 110), (ox, oy + 110)], fill=GOLD_DARK, outline=GOLD_MID)
    draw.rectangle([ox + 45, oy + 15, ox + 85, oy + 55], fill=(255, 245, 200, 220))
    for i in range(5):
        draw.line([(ox + 45 + i * 8, oy + 15), (ox + 65, oy + 55)], fill=(255, 230, 150, 120), width=2)
    draw.polygon([(ox + 20, oy + 95), (ox + 65, oy + 95), (ox + 42, oy + 110)], fill=(35, 45, 70))


def icon_representative(draw: ImageDraw.ImageDraw, ox: int, oy: int) -> None:
    for i, cx in enumerate([ox + 20, ox + 55, ox + 90]):
        gold_coin(draw, cx, oy + 85 - i * 10, 22 - i * 3)
    draw.line([(ox + 95, oy + 90), (ox + 95, oy + 35)], fill=GOLD_LIGHT, width=4)
    draw.polygon([(ox + 95, oy + 28), (ox + 115, oy + 48), (ox + 75, oy + 48)], fill=GOLD_LIGHT)
    gold_coin(draw, ox + 120, oy + 45, 26)
    draw.text((ox + 108, oy + 32), "財", font=load_font(24), fill=GOLD_SHADOW)


ICON_DRAWERS: dict[str, Callable[[ImageDraw.ImageDraw, int, int], None]] = {
    "rising": icon_rising,
    "dragon": icon_dragon,
    "handshake": icon_handshake,
    "scale": icon_scale,
    "piggy": icon_piggy,
    "envelope": icon_envelope,
    "horizon": icon_horizon,
    "representative": icon_representative,
}


def draw_icon(draw: ImageDraw.ImageDraw, icon: str) -> None:
    if icon == "number":
        return
    drawer = ICON_DRAWERS.get(icon)
    if drawer:
        drawer(draw, WIDTH - 250, 80)


def create_image(spec: FortuneImage, fortune_set: FortuneSet) -> Image.Image:
    img = Image.new("RGBA", (WIDTH, HEIGHT), NAVY_TOP)
    draw_vertical_gradient(img, NAVY_TOP, NAVY_BOTTOM)
    draw = ImageDraw.Draw(img, "RGBA")
    draw_constellation(draw, seed=(spec.index or 0) * 131 + 7)
    draw_mountains(draw)
    draw_ornate_frame(draw)
    draw_icon(draw, spec.icon)

    title_font = load_font(42 if spec.index is None else 38)
    draw_centered_white_text(draw, spec.title, 95, title_font, fill=WHITE)

    if spec.laurel:
        phrase_font = load_font(78 if spec.index is None else 68)
        tw, th = text_size(spec.phrase, phrase_font, draw)
        draw_laurel_banner(draw, WIDTH // 2, HEIGHT // 2 - 20, spec.phrase, phrase_font)
    elif spec.icon == "number":
        phrase_font = load_font(220)
        tw, th = text_size(spec.phrase, phrase_font, draw)
        draw_gold_text(draw, (WIDTH - tw) // 2, HEIGHT // 2 - th // 2 - 30, spec.phrase, phrase_font)
    else:
        phrase_font = load_font(86 if len(spec.phrase) <= 5 else 72)
        draw_centered_gold_text(draw, spec.phrase, HEIGHT // 2 - 10, phrase_font)

    caption_font = load_font(34)
    draw_centered_white_text(draw, spec.caption, HEIGHT - 175, caption_font, fill=WHITE_DIM, max_width=WIDTH - 140)

    return img.convert("RGB")


def generate_set(date_key: str) -> str:
    fortune_set = FORTUNE_SETS[date_key]
    output_dir = os.path.join(os.path.dirname(__file__), "images", date_key)
    os.makedirs(output_dir, exist_ok=True)
    for spec in fortune_set.images:
        img = create_image(spec, fortune_set)
        path = os.path.join(output_dir, spec.filename)
        img.save(path, "PNG", optimize=True)
        print(f"Created: {path} ({img.size[0]}x{img.size[1]})")
    print(f"\nDone! {len(fortune_set.images)} images saved to {output_dir}")
    return output_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate fortune horoscope images.")
    parser.add_argument(
        "--date",
        default="2025-06-18",
        choices=sorted(FORTUNE_SETS.keys()),
        help="Date key for the image set to generate",
    )
    args = parser.parse_args()
    ensure_font()
    generate_set(args.date)


if __name__ == "__main__":
    main()
