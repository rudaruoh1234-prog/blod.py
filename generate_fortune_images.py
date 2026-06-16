#!/usr/bin/env python3
"""Generate fortune horoscope social media images."""

from __future__ import annotations

import argparse
import math
import os
from dataclasses import dataclass, field

from PIL import Image, ImageDraw, ImageFont

FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts", "NotoSansKR.ttf")
WIDTH, HEIGHT = 1080, 1350
FONT_URL = (
    "https://github.com/google/fonts/raw/main/ofl/notosanskr/"
    "NotoSansKR%5Bwght%5D.ttf"
)


def ensure_font() -> str:
    if os.path.isfile(FONT_PATH):
        return FONT_PATH
    os.makedirs(os.path.dirname(FONT_PATH), exist_ok=True)
    import urllib.request

    urllib.request.urlretrieve(FONT_URL, FONT_PATH)
    return FONT_PATH


@dataclass
class FortuneImage:
    filename: str
    title: str
    phrase: str
    caption: str
    index: int | None = None  # None = representative image
    accent: tuple[int, int, int] = (212, 175, 55)


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
            FortuneImage(
                filename="00_representative.png",
                title="6월 10일 오늘의 운세",
                phrase="돈 들어올 가능성",
                caption="오늘 재물운이 강한 띠는 누구일까요",
                accent=(255, 215, 100),
            ),
            FortuneImage(
                filename="01_today_fortune.png",
                title="오늘 운세",
                phrase="핵심 요약",
                caption="재물운과 귀인운 흐름 분석",
                index=1,
                accent=(147, 197, 253),
            ),
            FortuneImage(
                filename="02_wealth_rank.png",
                title="재물운 순위",
                phrase="용띠 1위",
                caption="금전운 강한 띠 공개",
                index=2,
                accent=(250, 204, 21),
            ),
            FortuneImage(
                filename="03_case_study.png",
                title="실제 사례",
                phrase="환급금 확인",
                caption="예상 밖 입금 가능성",
                index=3,
                accent=(74, 222, 128),
            ),
            FortuneImage(
                filename="04_good_contact.png",
                title="좋은 연락",
                phrase="기회 발생",
                caption="새로운 수입 연결 가능",
                index=4,
                accent=(96, 165, 250),
            ),
            FortuneImage(
                filename="05_career.png",
                title="직장운",
                phrase="성과 인정",
                caption="좋은 평가 기대",
                index=5,
                accent=(167, 139, 250),
            ),
            FortuneImage(
                filename="06_benefactor.png",
                title="귀인운",
                phrase="도움 도착",
                caption="인연이 기회를 만듭니다",
                index=6,
                accent=(244, 114, 182),
            ),
            FortuneImage(
                filename="07_caution.png",
                title="주의사항",
                phrase="소비 점검",
                caption="충동 지출 주의",
                index=7,
                accent=(248, 113, 113),
            ),
            FortuneImage(
                filename="08_lucky_point.png",
                title="행운 포인트",
                phrase="숫자 8",
                caption="오늘의 행운 요소",
                index=8,
                accent=(251, 191, 36),
            ),
            FortuneImage(
                filename="09_usage.png",
                title="활용 방법",
                phrase="참고 활용",
                caption="운세를 현명하게 보는 법",
                index=9,
                accent=(52, 211, 153),
            ),
            FortuneImage(
                filename="10_summary.png",
                title="최종 정리",
                phrase="재물운 상승",
                caption="오늘의 핵심 운세 총정리",
                index=10,
                accent=(212, 175, 55),
            ),
        ],
    ),
    "2025-06-18": FortuneSet(
        date_label="2025. 06. 18",
        images=[
            FortuneImage(
                filename="00_representative.png",
                title="6월 18일 운세",
                phrase="재물운 상승",
                caption="귀인운과 재물운이 함께 움직이는 하루",
                accent=(255, 215, 100),
            ),
            FortuneImage(
                filename="01_today_overview.png",
                title="오늘 총운",
                phrase="상승 흐름",
                caption="오후로 갈수록 운세가 좋아지는 날",
                index=1,
                accent=(147, 197, 253),
            ),
            FortuneImage(
                filename="02_wealth.png",
                title="재물운",
                phrase="용띠 강세",
                caption="금전 기회가 확대될 가능성",
                index=2,
                accent=(250, 204, 21),
            ),
            FortuneImage(
                filename="03_benefactor.png",
                title="귀인운",
                phrase="인맥 활용",
                caption="좋은 사람을 통해 기회가 찾아옵니다",
                index=3,
                accent=(244, 114, 182),
            ),
            FortuneImage(
                filename="04_caution.png",
                title="주의 띠",
                phrase="신중 판단",
                caption="충동적인 선택은 피하는 것이 좋습니다",
                index=4,
                accent=(248, 113, 113),
            ),
            FortuneImage(
                filename="05_lucky_element.png",
                title="행운 요소",
                phrase="숫자 8",
                caption="오늘의 행운 포인트",
                index=5,
                accent=(251, 191, 36),
            ),
            FortuneImage(
                filename="06_money_management.png",
                title="재물 관리",
                phrase="지출 점검",
                caption="불필요한 소비를 줄이는 것이 중요",
                index=6,
                accent=(74, 222, 128),
            ),
            FortuneImage(
                filename="07_opportunity.png",
                title="기회 포착",
                phrase="연락 확인",
                caption="예상 밖 좋은 소식 가능성",
                index=7,
                accent=(96, 165, 250),
            ),
            FortuneImage(
                filename="08_summary.png",
                title="최종 정리",
                phrase="운의 흐름",
                caption="재물운과 귀인운을 함께 활용하는 하루",
                index=8,
                accent=(212, 175, 55),
            ),
        ],
    ),
}


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(ensure_font(), size)


def lerp_color(
    c1: tuple[int, int, int], c2: tuple[int, int, int], t: float
) -> tuple[int, int, int]:
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def draw_gradient(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    top: tuple[int, int, int],
    bottom: tuple[int, int, int],
) -> None:
    x0, y0, x1, y1 = box
    height = max(y1 - y0, 1)
    for y in range(y0, y1):
        t = (y - y0) / height
        color = lerp_color(top, bottom, t)
        draw.line([(x0, y), (x1, y)], fill=color)


def draw_radial_glow(
    img: Image.Image,
    center: tuple[int, int],
    radius: int,
    color: tuple[int, int, int, int],
) -> None:
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    cx, cy = center
    for r in range(radius, 0, -4):
        alpha = int(color[3] * (r / radius) ** 2)
        draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            fill=(color[0], color[1], color[2], alpha),
        )
    return Image.alpha_composite(img.convert("RGBA"), overlay)


def draw_stars(draw: ImageDraw.ImageDraw, seed: int, count: int = 40) -> None:
    import random

    rng = random.Random(seed)
    for _ in range(count):
        x = rng.randint(40, WIDTH - 40)
        y = rng.randint(40, HEIGHT - 40)
        size = rng.choice([2, 3, 4])
        alpha = rng.randint(40, 120)
        draw.ellipse([x, y, x + size, y + size], fill=(255, 255, 255, alpha))


def draw_star(
    draw: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
    radius: int,
    fill: tuple[int, ...],
) -> None:
    points = []
    for i in range(10):
        angle = math.radians(-90 + i * 36)
        r = radius if i % 2 == 0 else radius * 0.42
        points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(points, fill=fill)


def draw_decorative_rings(draw: ImageDraw.ImageDraw, accent: tuple[int, int, int]) -> None:
    for i, (cx, cy, r) in enumerate(
        [
            (WIDTH - 120, 180, 90),
            (100, HEIGHT - 200, 70),
            (WIDTH // 2, HEIGHT // 2 + 120, 220),
        ]
    ):
        width = 2 if i < 2 else 1
        color = (*accent, 35 + i * 15)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=width)


def wrap_text(
    text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw
) -> list[str]:
    words = list(text)
    lines: list[str] = []
    current = ""
    for ch in words:
        test = current + ch
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = ch
    if current:
        lines.append(current)
    return lines


def draw_centered_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    y: int,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, ...],
    max_width: int = WIDTH - 160,
    line_spacing: int = 12,
) -> int:
    lines = wrap_text(text, font, max_width, draw)
    total_height = 0
    line_heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        h = bbox[3] - bbox[1]
        line_heights.append(h)
        total_height += h
    total_height += line_spacing * max(len(lines) - 1, 0)
    current_y = y
    for line, h in zip(lines, line_heights):
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        x = (WIDTH - w) // 2
        draw.text((x, current_y), line, font=font, fill=fill)
        current_y += h + line_spacing
    return current_y


def create_image(spec: FortuneImage, fortune_set: FortuneSet) -> Image.Image:
    base_top = (18, 12, 48)
    base_bottom = (8, 6, 28)
    img = Image.new("RGBA", (WIDTH, HEIGHT), base_top)
    draw = ImageDraw.Draw(img)
    draw_gradient(draw, (0, 0, WIDTH, HEIGHT), base_top, base_bottom)

    img = draw_radial_glow(img, (WIDTH // 2, 420), 500, (*spec.accent, 55))
    img = draw_radial_glow(img, (180, 900), 280, (120, 80, 200, 35))
    draw = ImageDraw.Draw(img)
    draw_stars(draw, seed=(spec.index or 0) * 97 + 13)

    # Top bar
    draw.rounded_rectangle(
        [60, 60, WIDTH - 60, 130],
        radius=20,
        fill=(255, 255, 255, 18),
        outline=(*spec.accent, 90),
        width=2,
    )

    date_font = load_font(34)
    if spec.index is None:
        date_text = fortune_set.date_label
    else:
        date_text = f"오늘의 운세 · {spec.index}/{fortune_set.slide_count}"
    bbox = draw.textbbox((0, 0), date_text, font=date_font)
    draw.text(
        ((WIDTH - (bbox[2] - bbox[0])) // 2, 82),
        date_text,
        font=date_font,
        fill=(230, 230, 240, 220),
    )

    # Index badge
    if spec.index is not None:
        badge_font = load_font(42)
        badge_text = f"{spec.index:02d}"
        badge_size = 88
        bx, by = WIDTH - 60 - badge_size, 155
        draw.ellipse(
            [bx, by, bx + badge_size, by + badge_size],
            fill=(*spec.accent, 40),
            outline=spec.accent,
            width=3,
        )
        bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(
            (bx + (badge_size - tw) // 2, by + (badge_size - th) // 2 - 4),
            badge_text,
            font=badge_font,
            fill=(255, 255, 255, 255),
        )
    else:
        # Representative badge
        badge_font = load_font(30)
        badge_text = "TODAY"
        draw.rounded_rectangle(
            [WIDTH // 2 - 70, 155, WIDTH // 2 + 70, 205],
            radius=16,
            fill=(*spec.accent, 50),
            outline=spec.accent,
            width=2,
        )
        bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
        draw.text(
            (WIDTH // 2 - (bbox[2] - bbox[0]) // 2, 163),
            badge_text,
            font=badge_font,
            fill=(255, 255, 255, 255),
        )

    draw_decorative_rings(draw, spec.accent)

    # Main card
    card_top, card_bottom = 250, 1080
    draw.rounded_rectangle(
        [70, card_top, WIDTH - 70, card_bottom],
        radius=36,
        fill=(20, 16, 45, 140),
        outline=(*spec.accent, 90),
        width=2,
    )

    # Title label
    label_font = load_font(28)
    draw.text((140, card_top + 42), "제목", font=label_font, fill=(*spec.accent, 220))

    title_font = load_font(56 if spec.index is None else 50)
    y = draw_centered_text(
        draw,
        spec.title,
        y=card_top + 78,
        font=title_font,
        fill=(255, 255, 255, 255),
    )

    # Divider
    div_y = y + 36
    div_w = 120
    draw.line(
        [(WIDTH // 2 - div_w, div_y), (WIDTH // 2 + div_w, div_y)],
        fill=spec.accent,
        width=4,
    )

    # Phrase label
    draw.text((140, div_y + 28), "문구", font=label_font, fill=(*spec.accent, 220))

    # Main phrase
    phrase_font = load_font(88 if spec.index is None else 76)
    phrase_y = div_y + 64
    y = draw_centered_text(
        draw,
        spec.phrase,
        y=phrase_y,
        font=phrase_font,
        fill=spec.accent,
        max_width=WIDTH - 140,
        line_spacing=16,
    )

    draw_star(draw, WIDTH // 2, y + 42, 18, (*spec.accent, 200))

    # Caption box
    caption_top = card_bottom - 200
    draw.rounded_rectangle(
        [110, caption_top, WIDTH - 110, card_bottom - 50],
        radius=24,
        fill=(0, 0, 0, 45),
        outline=(255, 255, 255, 40),
        width=1,
    )
    caption_label_font = load_font(28)
    draw.text((140, caption_top + 22), "캡션", font=caption_label_font, fill=(*spec.accent, 200))
    caption_font = load_font(38)
    draw_centered_text(
        draw,
        spec.caption,
        y=caption_top + 62,
        font=caption_font,
        fill=(240, 240, 245, 240),
        max_width=WIDTH - 220,
        line_spacing=10,
    )

    # Bottom branding
    brand_font = load_font(26)
    brand = "오늘의 운세"
    bbox = draw.textbbox((0, 0), brand, font=brand_font)
    draw.text(
        ((WIDTH - (bbox[2] - bbox[0])) // 2, HEIGHT - 90),
        brand,
        font=brand_font,
        fill=(180, 180, 200, 160),
    )

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
