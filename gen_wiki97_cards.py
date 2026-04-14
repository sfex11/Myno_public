#!/usr/bin/env python3
"""Generate 6 card-news images for Wiki 97 blog post."""

from PIL import Image, ImageDraw, ImageFont
import textwrap, os, sys

# === Config ===
W, H = 1080, 1350
SPLIT_Y = H // 2  # 675
FONT_PATH = "/system/fonts/NotoSansCJK-Regular.ttc"
ASSET_DIR = "/data/data/com.termux/files/home/.hermes/skills/card-news/assets"
OUT_DIR = os.path.expanduser("~/Myno_public/assets")

# Colors
WHITE = "#FFFFFF"
CREAM = "#EDE8DC"
BRAND = "#E8801A"
TITLE_CLR = "#1A1A1A"
BODY_CLR = "#3D3D3D"
BORDER_CLR = "#1A1A1A"

# Fonts
font_title = ImageFont.truetype(FONT_PATH, 72, index=0)
font_body = ImageFont.truetype(FONT_PATH, 34, index=0)
font_bullet = ImageFont.truetype(FONT_PATH, 34, index=0)
font_brand = ImageFont.truetype(FONT_PATH, 28, index=0)
font_page = ImageFont.truetype(FONT_PATH, 28, index=0)
font_small = ImageFont.truetype(FONT_PATH, 26, index=0)

MARGIN_L = 72
MARGIN_R = 72
TEXT_START_Y = SPLIT_Y + 48
TEXT_WIDTH = W - MARGIN_L - MARGIN_R


def draw_rounded_rect(draw, xy, radius, fill=None, outline=None, width=1):
    x0, y0, x1, y1 = xy
    r = radius
    # corners
    draw.ellipse([x0, y0, x0+2*r, y0+2*r], fill=fill, outline=outline, width=width)
    draw.ellipse([x1-2*r, y0, x1, y0+2*r], fill=fill, outline=outline, width=width)
    draw.ellipse([x0, y1-2*r, x0+2*r, y1], fill=fill, outline=outline, width=width)
    draw.ellipse([x1-2*r, y1-2*r, x1, y1], fill=fill, outline=outline, width=width)
    # rects between corners
    draw.rectangle([x0+r, y0, x1-r, y0+r], fill=fill)  # top
    draw.rectangle([x0+r, y1-r, x1-r, y1], fill=fill)  # bottom
    draw.rectangle([x0, y0+r, x0+r, y1-r], fill=fill)  # left
    draw.rectangle([x1-r, y0+r, x1, y1-r], fill=fill)  # right
    draw.rectangle([x0+r, y0+r, x1-r, y1-r], fill=fill)  # center
    # outline edges
    if outline:
        draw.arc([x0, y0, x0+2*r, y0+2*r], 180, 270, fill=outline, width=width)
        draw.arc([x1-2*r, y0, x1, y0+2*r], 270, 360, fill=outline, width=width)
        draw.arc([x0, y1-2*r, x0+2*r, y1], 90, 180, fill=outline, width=width)
        draw.arc([x1-2*r, y1-2*r, x1, y1], 0, 90, fill=outline, width=width)
        draw.line([x0+r, y0, x1-r, y0], fill=outline, width=width)
        draw.line([x0+r, y1, x1-r, y1], fill=outline, width=width)
        draw.line([x0, y0+r, x0, y1-r], fill=outline, width=width)
        draw.line([x1, y0+r, x1, y1-r], fill=outline, width=width)


def load_myno(pose, max_h=400):
    path = os.path.join(ASSET_DIR, f"myno_{pose}.png")
    img = Image.open(path).convert("RGBA")
    ratio = max_h / img.height
    if ratio < 1:
        img = img.resize((int(img.width * ratio), int(img.height * ratio)), Image.LANCZOS)
    return img


def wrap_text(text, font, max_width, draw):
    """Word-wrap text to fit within max_width pixels."""
    lines = []
    for paragraph in text.split('\n'):
        if not paragraph.strip():
            lines.append('')
            continue
        chars = list(paragraph)
        current = ''
        for ch in chars:
            test = current + ch
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] > max_width and current:
                lines.append(current)
                current = ch
            else:
                current = test
        if current:
            lines.append(current)
    return lines


def create_card(card_num, title, body, points, pose, page_str, out_path, subtitle=None):
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)

    # Bottom half: cream background
    draw.rectangle([0, SPLIT_Y, W, H], fill=CREAM)

    # Header box (illustration area)
    box_margin = 40
    box_x0, box_y0 = box_margin, box_margin
    box_x1, box_y1 = W - box_margin, SPLIT_Y - 20
    draw_rounded_rect(draw, (box_x0, box_y0, box_x1, box_y1),
                      radius=16, fill=WHITE, outline=BORDER_CLR, width=3)

    # Place Myno character in header box
    myno = load_myno(pose, max_h=min(380, box_y1 - box_y0 - 40))
    mx = (W - myno.width) // 2
    my = box_y0 + (box_y1 - box_y0 - myno.height) // 2
    img.paste(myno, (mx, my), myno)

    # Brand tag top-left inside box
    draw.text((box_x0 + 20, box_y0 + 14), "Myno News", font=font_brand, fill=BRAND)

    # Page number top-right inside box
    bbox_page = draw.textbbox((0, 0), page_str, font=font_page)
    pw = bbox_page[2] - bbox_page[0]
    draw.text((box_x1 - 20 - pw, box_y0 + 14), page_str, font=font_page, fill="#999999")

    # === Text area (bottom half) ===
    y = TEXT_START_Y

    # Title
    title_lines = wrap_text(title, font_title, TEXT_WIDTH, draw)
    for line in title_lines:
        draw.text((MARGIN_L, y), line, font=font_title, fill=TITLE_CLR)
        y += 84
    y += 12

    # Subtitle (if any)
    if subtitle:
        sub_lines = wrap_text(subtitle, font_small, TEXT_WIDTH, draw)
        for line in sub_lines:
            draw.text((MARGIN_L, y), line, font=font_small, fill=BRAND)
            y += 34
        y += 8

    # Body
    if body:
        body_lines = wrap_text(body, font_body, TEXT_WIDTH, draw)
        for line in body_lines:
            draw.text((MARGIN_L, y), line, font=font_body, fill=BODY_CLR)
            y += 44
        y += 16

    # Divider line
    draw.line([(MARGIN_L, y), (W - MARGIN_R, y)], fill=BRAND, width=3)
    y += 24

    # Bullet points
    if points:
        bullet_items = points.split("|")
        for item in bullet_items:
            item = item.strip()
            if not item:
                continue
            # Orange bullet dot
            dot_y = y + 14
            draw.ellipse([MARGIN_L, dot_y, MARGIN_L + 12, dot_y + 12], fill=BRAND)
            # Text
            bullet_lines = wrap_text(item, font_bullet, TEXT_WIDTH - 28, draw)
            for i, line in enumerate(bullet_lines):
                draw.text((MARGIN_L + 28, y), line, font=font_bullet, fill=BODY_CLR)
                y += 44
            y += 8

    # Save
    img.save(out_path, "PNG")
    print(f"Saved: {out_path}")


# === Card definitions ===
cards = [
    {
        "num": 1,
        "title": "97편의 지도가 그리는 것",
        "subtitle": "Myno News",
        "body": "LLM Agent 합성 분석\n모델을 더 크게에서\n시스템을 더 똑똑하게로",
        "points": "97편 논문|25쌍 교차 참조|6개 합성 분석 페이지",
        "pose": "curious",
        "page": "01/06",
        "out": os.path.join(OUT_DIR, "card_wiki97_01.png"),
    },
    {
        "num": 2,
        "title": "왜 합성 분석인가?",
        "body": "단순 요약이 아니다. 97편이 함께 말하는 것을 찾는다. 일치점, 모순점, 보완 관계, 시간에 따른 트렌드까지.",
        "points": "Ingest > Entity Enrichment > Compound > Cross-reference|시간이 지날수록 Wiki가 스스로 진화",
        "pose": "sitting",
        "page": "02/06",
        "out": os.path.join(OUT_DIR, "card_wiki97_02.png"),
    },
    {
        "num": 3,
        "title": "LLM Agent 연구 4대 축",
        "body": "Claude가 97편을 분석하여 도출한 핵심 연구 축",
        "points": "축 1: 평가의 현실화 -- 시뮬레이션에서 라이브 플랫폼으로|축 2: 구조/메타인지 -- Less LLM, More Structure|축 3: 보안/거버넌스 -- 출력에서 궤적/인프라로|축 4: 통합 아키텍처 -- 상태 공유와 협조 프로토콜",
        "pose": "waving",
        "page": "03/06",
        "out": os.path.join(OUT_DIR, "card_wiki97_03.png"),
    },
    {
        "num": 4,
        "title": "3가지 트렌드",
        "body": "연구 방향의 패러다임 전환",
        "points": "평가 무게중심 이동: 시뮬레이션 > 라이브 플랫폼|Less LLM, More Structure: 파라미터 > 아키텍처|보안 수직 확장: 프롬프트 > 궤적 > 인프라",
        "pose": "walking",
        "page": "04/06",
        "out": os.path.join(OUT_DIR, "card_wiki97_04.png"),
    },
    {
        "num": 5,
        "title": "3가지 핵심 논점",
        "body": "97편도 결론을 내리지 못한 문제들",
        "points": "구조 vs 모델 -- 비선형 상호작용 미해결|자율성 vs 통제 -- 본질적 긴장 관계|현실 평가의 역설 -- 라이브 평가 고유 한계",
        "pose": "coffee",
        "page": "05/06",
        "out": os.path.join(OUT_DIR, "card_wiki97_05.png"),
    },
    {
        "num": 6,
        "title": "모델이 아닌 시스템으로",
        "body": "LLM 에이전트의 병목은 모델 크기가 아니라 시스템 설계에 있다. 메타인지, 상태 공유, 궤적 보안, 라이브 평가를 동시에 설계하는 것이 다음 단계다.",
        "points": "PSI 공유 상태 패턴이 멀티에이전트 표준으로|ActWisely 메타인지가 에이전트 필수 요건으로|97편의 단편적 인사이트가 새로운 통찰을 생성",
        "pose": "stretching",
        "page": "06/06",
        "out": os.path.join(OUT_DIR, "card_wiki97_06.png"),
    },
]

if __name__ == "__main__":
    for c in cards:
        create_card(
            card_num=c["num"],
            title=c["title"],
            body=c.get("body", ""),
            points=c.get("points", ""),
            pose=c["pose"],
            page_str=c["page"],
            out_path=c["out"],
            subtitle=c.get("subtitle"),
        )
    print("All 6 cards generated!")
