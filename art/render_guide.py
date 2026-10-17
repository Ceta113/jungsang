"""삼신 가챠 '작동 방식' 안내 이미지 (1080x2600). render_gacha.py를 먼저 돌려 art/out의 알 이미지가 있어야 한다.

  python art/render_guide.py
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage as ndi

sys.argv.append("--quick")            # render_gacha의 무거운 2x 그리드를 만들지 않게
from render_gacha import TIERS, stroke_paint  # noqa: E402

ART = Path(__file__).parent / "out"
W, H = 1080, 2600
FB = "C:/Windows/Fonts/malgunbd.ttf"
FR = "C:/Windows/Fonts/malgun.ttf"
TXT = (232, 229, 222)
MUTED = (150, 152, 165)
LINE = (70, 72, 86)


def tier_rgb(t):
    if t == "비정상":
        return (236, 234, 228)
    return tuple(int(v) for v in np.clip(TIERS[t]["col"] * 255, 0, 255))


def paint_bg():
    rng = np.random.default_rng(3)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    t = yy / H
    base = np.stack([0.030 + 0.025 * t, 0.034 + 0.028 * t, 0.055 + 0.040 * t], -1)
    n = ndi.zoom(rng.random((H // 120 + 3, W // 120 + 3)), 120, order=3)[:H, :W]
    n2 = ndi.zoom(rng.random((H // 40 + 3, W // 40 + 3)), 40, order=3)[:H, :W]
    base *= (0.75 + 0.35 * n + 0.15 * n2)[..., None]
    glow = np.exp(-(((xx - 540) / 600) ** 2 + ((yy - 300) / 380) ** 2))
    base += np.array([0.10, 0.075, 0.03]) * glow[..., None] * 0.6
    src = np.clip(base, 0, 1).astype(np.float32)
    return stroke_paint(src, [(18, 0.012, 7, 235), (9, 0.010, 9, 220)], seed=11)


def egg_icon(no, tier, size):
    im = Image.open(ART / f"egg_{no}_{tier}.png").convert("RGB")
    s = im.size[0] / 1024
    im = im.crop((int(300 * s), int(175 * s), int(724 * s), int(680 * s))).resize((int(size * 0.84), size), Image.LANCZOS)
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).ellipse([6, 6, im.size[0] - 6, im.size[1] - 6], fill=255)
    return im, m.filter(ImageFilter.GaussianBlur(8))


def main():
    bg = paint_bg()
    im = Image.fromarray((np.clip(bg, 0, 1) * 255 + 0.5).astype(np.uint8))
    d = ImageDraw.Draw(im)
    f = lambda p, s: ImageFont.truetype(p, s)  # noqa: E731

    def center(y, text, font, fill):
        d.text(((W - d.textlength(text, font=font)) / 2, y), text, font=font, fill=fill)

    def section(y, title):
        d.text((80, y), title, font=f(FB, 40), fill=TXT)
        d.line([(80, y + 62), (W - 80, y + 62)], fill=LINE, width=2)
        return y + 86

    center(70, "삼신 가챠", f(FB, 84), (245, 214, 150))
    center(180, "알이 깨지면 인생이 정해진다 — 작동 방식", f(FR, 34), MUTED)

    # 1. 언제
    y = section(270, "1  언제 알이 내려오나")
    rows = [("0살 · 출생 5연차", "아빠 1 · 엄마 1 · 재능 3, 한 장씩 순서대로"),
            ("성장 가챠 4회", "초·중·고 입학, 성인(만 19세) — 재능 or 인연"),
            ("복(福) 100", "추가 1회. 복은 1년에 최대 60까지 쌓인다")]
    for a, b in rows:
        d.text((100, y), "•", font=f(FB, 32), fill=(245, 214, 150))
        d.text((135, y), a, font=f(FB, 32), fill=TXT)
        d.text((135, y + 44), b, font=f(FR, 28), fill=MUTED)
        y += 98

    # 2. 등급
    y = section(y + 24, "2  등급과 확률 (기본)")
    pct = {"정상": "60%", "준수": "25%", "희귀": "10.5%", "전설": "3.5%", "비정상": "1%"}
    desc = {"정상": "희뿌연 흰빛 · 꽝이 아니라 평범한 따뜻함",
            "준수": "맑은 파란빛 · 스탯 +8, 성장 ×1.1",
            "희귀": "보랏빛 번개 · +15, 성장 ×1.25",
            "전설": "금빛이 쏟아진다 · +25, 성장 ×1.5",
            "비정상": "빛이 거꾸로 빨려 든다 · 초현실 효과 + 대가"}
    for tier, P in TIERS.items():
        ic, m = egg_icon(P["no"], tier, 104)
        im.paste(ic, (90, y - 6), m)
        c = tier_rgb(tier)
        d.text((200, y + 2), f"{tier}  {P['stars']}", font=f(FB, 34), fill=c)
        pw = d.textlength(pct[tier], font=f(FB, 40))
        d.text((W - 90 - pw, y), pct[tier], font=f(FB, 40), fill=c)
        d.text((200, y + 50), desc[tier], font=f(FR, 26), fill=MUTED)
        y += 118
    d.text((90, y + 2), "천장까지 합친 실효 확률(20만 명 시뮬): 희귀 13.8% · 전설 4.6%", font=f(FR, 25), fill=MUTED)
    y += 50

    # 3. 천장
    y = section(y + 20, "3  천장 — 삼신할미의 눈치")
    rules = ["정상·준수가 나올 때마다 눈치 +1 → 희귀 +1.5%p, 전설 +0.5%p",
             "눈치 10 → 다음 1장 희귀 이상 확정",
             "전설 없이 30장 → 다음 1장 전설 확정",
             "출생 5연차가 '정상'만 5장일 수는 없다"]
    for r in rules:
        d.text((100, y), "•", font=f(FB, 30), fill=(245, 214, 150))
        d.text((135, y), r, font=f(FR, 29), fill=TXT)
        y += 52
    # 게이지 그림
    gx0, gy0 = 135, y + 10
    for i in range(10):
        on = i < 6
        x = gx0 + i * 76
        d.rounded_rectangle([x, gy0, x + 62, gy0 + 22], 6, fill=(245, 214, 150) if on else (52, 54, 66))
    d.text((gx0, gy0 + 34), "눈치 6/10 — 다음 희귀 확률 19.5%", font=f(FR, 25), fill=MUTED)
    y = gy0 + 86

    # 4. 연출
    y = section(y + 10, "4  한 장이 깨지는 순서")
    sheet = Image.open(ART / "sequence_전설.png").convert("RGB")
    s = (sheet.size[0] - 12) // 2
    caps = ["① 강림", "② 균열", "③ 승급", "④ 개화"]
    tw = 214
    for i in range(4):
        tile = sheet.crop(((i % 2) * (s + 12), (i // 2) * (s + 12), (i % 2) * (s + 12) + s, (i // 2) * (s + 12) + s))
        tile = tile.crop((int(s * 0.12), int(s * 0.10), int(s * 0.88), int(s * 0.86))).resize((tw, tw), Image.LANCZOS)
        x = 80 + i * (tw + 16)
        im.paste(tile, (x, y))
        d.rectangle([x, y, x + tw, y + tw], outline=LINE, width=2)
        cw = d.textlength(caps[i], font=f(FB, 28))
        d.text((x + (tw - cw) / 2, y + tw + 10), caps[i], font=f(FB, 28), fill=TXT)
    y += tw + 56
    for r in ["빛의 색 = 등급 예고. 희귀 이상은 3분의 1 확률로 한 단계 낮은 색에서 '승급'",
              "비정상은 늘 흰빛(정상)인 척하다가, 빛이 거꾸로 빨려 들어간다"]:
        d.text((90, y), r, font=f(FR, 26), fill=MUTED)
        y += 42

    # 5. 중복
    y = section(y + 18, "5  겹치면")
    for a, b in [("같은 재능 또 나옴", "각성 — 한 등급 위로 (전설 → 전설+)"),
                 ("비정상이 두 번", "서로 상쇄돼서 둘 다 사라지고, 다시 '정상'")]:
        d.text((100, y), a, font=f(FB, 30), fill=TXT)
        d.text((430, y + 2), b, font=f(FR, 28), fill=MUTED)
        y += 54

    center(H - 70, "정상 · 삼신 가챠", f(FR, 24), (110, 112, 126))
    im.save(ART / "guide_작동방식.png")
    print("saved guide_작동방식.png, last y =", y)


if __name__ == "__main__":
    main()
