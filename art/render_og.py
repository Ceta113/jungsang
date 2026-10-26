"""웹사이트 대표 이미지(og:image, 1200×630) → web/og.png

  python art/render_og.py

오른쪽은 전설·상 단계 이미지(라벨 위까지 잘라 씀), 왼쪽은 사이트와 같은 다크 바탕 + 금빛 제목.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
W, H = 1200, 630
BG = (13, 15, 21)
INK = (235, 231, 223)
MUTED = (141, 145, 162)
ACCENT = (239, 205, 140)
TIERS = [("재앙", "#d8432b"), ("실패", "#b49a72"), ("정상", "#f3e6cf"), ("준수", "#4aa0ff"),
         ("희귀", "#ad60ff"), ("전설", "#ffb43e"), ("신화", "#e9e4ff"), ("비정상", "#ffffff")]


def font(name, size, weight=None):
    f = ImageFont.truetype(f"C:/Windows/Fonts/{name}", size)
    if weight:
        f.set_variation_by_name(weight)
    return f


def main():
    canvas = Image.new("RGB", (W, H), BG)

    # 종이 결: 사이트 배경과 같은 텍스처를 옅게
    tex = Image.open(ROOT / "web/img/tex.webp").convert("L")
    grain = Image.new("L", (W, H))
    for x in range(0, W, tex.width):
        for y in range(0, H, tex.height):
            grain.paste(tex, (x, y))
    g = (np.asarray(grain, np.float32) / 255 - 0.5) * 10
    canvas = Image.fromarray(np.clip(np.asarray(canvas, np.float32) + g[..., None], 0, 255).astype(np.uint8))

    # 오른쪽: 전설·상 알. 아래 라벨(y≈900~)은 빼고 위쪽 880px만
    art = Image.open(ROOT / "art/out/steps/18_전설_상.png").convert("RGB").crop((72, 0, 952, 880)).resize((H, H), Image.LANCZOS)
    x0 = W - H
    a = np.asarray(art, np.float32)
    base = np.asarray(canvas, np.float32)[:, x0:]
    xs = np.linspace(0, 1, H)[None, :, None]
    ys = np.linspace(0, 1, H)[:, None, None]
    m = np.clip(xs / 0.42, 0, 1) ** 1.6 * np.clip((1 - ys) / 0.18, 0, 1) ** 0.8  # 왼쪽·아래로 바탕에 녹아들게
    mixed = base * (1 - m) + a * m
    canvas.paste(Image.fromarray(mixed.astype(np.uint8)), (x0, 0))

    d = ImageDraw.Draw(canvas)
    d.text((72, 128), "삼신 가챠", font=font("NotoSerifKR-VF.ttf", 112, "Bold"), fill=ACCENT)
    sub = font("NotoSansKR-VF.ttf", 30, "Medium")
    d.text((76, 292), "알을 깨면 부모와 재능이 정해진다", font=sub, fill=INK)
    d.text((76, 338), "크랙 인생 시뮬레이션 「정상」 가챠 실행기", font=font("NotoSansKR-VF.ttf", 24, "Regular"), fill=MUTED)

    # 등급 사다리: 재앙→신화 7단은 이어지고, 비정상은 사다리 밖의 별도 등급이라 '+'로 붙인다
    small = font("NotoSansKR-VF.ttf", 22, "Bold")
    x, y = 76, 430
    for i, (name, col) in enumerate(TIERS):
        d.text((x, y), name, font=small, fill=col)
        x += d.textlength(name, font=small)
        sep = "›" if i < len(TIERS) - 2 else "+" if i == len(TIERS) - 2 else None
        if sep:
            d.text((x + (6 if sep == "›" else 14), y), sep, font=small, fill=MUTED)
            x += 26 if sep == "›" else 44
    d.text((76, 548), "ceta113.github.io/jungsang", font=font("NotoSansKR-VF.ttf", 20, "Regular"), fill=MUTED)

    out = ROOT / "web/og.png"
    canvas.save(out, optimize=True)
    print(out, f"{out.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
