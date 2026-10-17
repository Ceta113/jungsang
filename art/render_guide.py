"""삼신 가챠 '작동 방식' 안내 이미지 (1080 x 4100, 세로 스크롤용).
render_gacha.py를 먼저 돌려 art/out/steps와 sequence 이미지가 있어야 한다.

  python art/render_guide.py
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage as ndi

sys.argv.append("--quick")            # render_gacha의 무거운 2x 그리드를 만들지 않게
from render_gacha import FAMS, LADDER, stroke_paint  # noqa: E402

ART = Path(__file__).parent / "out"
W, H = 1080, 4100
FB = "C:/Windows/Fonts/malgunbd.ttf"
FR = "C:/Windows/Fonts/malgun.ttf"
TXT = (232, 229, 222)
MUTED = (150, 152, 165)
LINE = (70, 72, 86)
GOLD = (245, 214, 150)
BASE_PCT = {"신화": "0.5%", "전설": "3.5%", "희귀": "11%", "준수": "24%", "정상": "45%",
            "실패": "12%", "재앙": "3%", "비정상": "1%"}
SPLIT = {"재앙": "하 15 · 중 35 · 상 50", "실패": "하 15 · 중 35 · 상 50", "정상": "하 30 · 중 40 · 상 30",
         "준수": "하 50 · 중 35 · 상 15", "희귀": "하 50 · 중 35 · 상 15", "전설": "하 55 · 중 33 · 상 12",
         "신화": "하 60 · 중 32 · 상 8", "비정상": "미세 60 · 뚜렷 30 · 세계급 10"}
DESC = {"신화": "진주빛, 하늘이 열린다 · +38~+55, 성장 ×1.8~2.5",
        "전설": "금빛이 쏟아진다 · +24~+32, 성장 ×1.4~1.6",
        "희귀": "보랏빛 번개 · +14~+20, 성장 ×1.2~1.3",
        "준수": "맑은 파란빛 · +7~+11, 성장 ×1.05~1.15",
        "정상": "희뿌연 흰빛 · +1~+5 · 꽝이 아니라 평범한 따뜻함",
        "실패": "김빠진 빛, 알이 굴러떨어진다 · -2~-8",
        "재앙": "검붉은 그을음과 연기 · -10~-20",
        "비정상": "등급 바깥 · 초현실 효과 + 대가"}


def paint_bg():
    rng = np.random.default_rng(3)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    t = yy / H
    base = np.stack([0.030 + 0.020 * t, 0.034 + 0.022 * t, 0.055 + 0.030 * t], -1)
    n = ndi.zoom(rng.random((H // 120 + 3, W // 120 + 3)), 120, order=3)[:H, :W]
    n2 = ndi.zoom(rng.random((H // 40 + 3, W // 40 + 3)), 40, order=3)[:H, :W]
    base *= (0.75 + 0.35 * n + 0.15 * n2)[..., None]
    base += np.array([0.10, 0.075, 0.03]) * np.exp(-(((xx - 540) / 600) ** 2 + ((yy - 300) / 380) ** 2))[..., None] * 0.6
    return stroke_paint(np.clip(base, 0, 1).astype(np.float32), [(18, 0.012, 7, 235), (9, 0.010, 9, 220)], seed=11)


def step_img(fam, sub):
    return next((ART / "steps").glob(f"*_{fam}_{sub}.png"))


def egg_icon(fam, size):
    sub = "뚜렷" if fam == "비정상" else "중"
    im = Image.open(step_img(fam, sub)).convert("RGB")
    s = im.size[0] / 1024
    im = im.crop((int(262 * s), int(150 * s), int(762 * s), int(700 * s))).resize((int(size * 0.91), size), Image.LANCZOS)
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).ellipse([6, 6, im.size[0] - 6, im.size[1] - 6], fill=255)
    return im, m.filter(ImageFilter.GaussianBlur(8))


def main():
    im = Image.fromarray((np.clip(paint_bg(), 0, 1) * 255 + 0.5).astype(np.uint8))
    d = ImageDraw.Draw(im)
    f = lambda p, s: ImageFont.truetype(p, s)  # noqa: E731

    def center(y, text, font, fill):
        d.text(((W - d.textlength(text, font=font)) / 2, y), text, font=font, fill=fill)

    def section(y, title):
        d.text((80, y), title, font=f(FB, 40), fill=TXT)
        d.line([(80, y + 62), (W - 80, y + 62)], fill=LINE, width=2)
        return y + 86

    def bullets(y, rows, size=29, gap=50):
        for r in rows:
            d.text((100, y), "•", font=f(FB, size), fill=GOLD)
            d.text((135, y), r, font=f(FR, size), fill=TXT)
            y += gap
        return y

    center(70, "삼신 가챠", f(FB, 84), GOLD)
    center(180, "알이 깨지면 인생이 정해진다 — 작동 방식", f(FR, 34), MUTED)

    y = section(270, "1  언제 알이 내려오나")
    for a, b in [("0살 · 출생 5연차", "아빠 1 · 엄마 1 · 재능 3, 한 장씩 순서대로"),
                 ("성장 가챠 4회", "초·중·고 입학, 성인(만 19세) — 재능 or 인연"),
                 ("복(福) 100", "추가 1회. 복은 1년에 최대 60 (실패 보상은 별도)")]:
        d.text((100, y), "•", font=f(FB, 32), fill=GOLD)
        d.text((135, y), a, font=f(FB, 32), fill=TXT)
        d.text((135, y + 44), b, font=f(FR, 28), fill=MUTED)
        y += 98

    # 2. 사다리
    y = section(y + 24, "2  21단계 사다리 (7등급 × 하·중·상)")
    bx0, bw = 90, (W - 180) / 21
    for i in range(21):
        fam = LADDER[i // 3]
        c = FAMS[fam]["text"]
        shade = 0.55 + 0.225 * (i % 3)
        cc = tuple(int(v * shade) for v in c)
        d.rectangle([bx0 + i * bw + 2, y, bx0 + (i + 1) * bw - 2, y + 44], fill=cc)
        if i % 3 == 1:
            tw = d.textlength(fam, font=f(FB, 24))
            d.text((bx0 + i * bw + bw / 2 - tw / 2, y + 54), fam, font=f(FB, 24), fill=c)
    d.text((bx0, y + 92), "1단계", font=f(FR, 22), fill=MUTED)
    d.text((W - 90 - d.textlength("21단계", font=f(FR, 22)), y + 92), "21단계", font=f(FR, 22), fill=MUTED)
    y += 140
    for fam in ["신화", "전설", "희귀", "준수", "정상", "실패", "재앙", "비정상"]:
        ic, m = egg_icon(fam, 104)
        im.paste(ic, (90, y - 6), m)
        c = FAMS[fam]["text"]
        d.text((200, y - 2), f"{fam}  {FAMS[fam]['mark']}", font=f(FB, 34), fill=c)
        pw = d.textlength(BASE_PCT[fam], font=f(FB, 40))
        d.text((W - 90 - pw, y - 4), BASE_PCT[fam], font=f(FB, 40), fill=c)
        d.text((200, y + 44), DESC[fam], font=f(FR, 25), fill=MUTED)
        d.text((200, y + 76), "세부 " + SPLIT[fam], font=f(FR, 23), fill=(120, 122, 136))
        y += 124
    d.text((90, y + 4), "1차 굴림 기본 확률. 천장 포함 실효: 실패 10.1% · 재앙 2.2% · 신화 0.6%",
           font=f(FR, 23), fill=MUTED)
    y += 50

    # 3. 굴림
    y = section(y + 20, "3  두 번 굴린다")
    y = bullets(y, ["1차 1~10000 → 등급 (눈치 게이지별 구간표)",
                    "2차 1~100 → 하·중·상",
                    "굴림값은 카드에 그대로 찍힌다. 결과를 서사에 맞춰 바꾸지 않는다"])

    # 4. 실패
    y = section(y + 20, "4  실패해도 남는 것")
    y = bullets(y, ["삼신의 사과 — 실패 복 +10, 재앙 복 +25",
                    "실패·재앙은 눈치 +2 → 다음 장의 희귀 이상 확률이 오른다",
                    "극복 조건을 이루면 카드가 뒤집힌다",
                    "    실패 → 준수, 재앙 → 희귀 (하·중·상 유지)",
                    "출생에서 재앙은 한 번만. 두 번째는 실패·하로 감면"])

    # 5. 천장
    y = section(y + 20, "5  천장 — 삼신할미의 눈치")
    y = bullets(y, ["재앙·실패 +2 / 정상·준수 +1 / 희귀 이상이 나오면 0",
                    "눈치 1당 희귀 +1.2%p · 전설 +0.35%p · 신화 +0.05%p",
                    "눈치 10 → 다음 1장 희귀 이상 확정",
                    "전설·신화 없이 40장 → 다음 1장 전설 확정",
                    "출생 5연차에 준수 이상이 하나도 없을 수는 없다"])
    gx0, gy0 = 135, y + 6
    for i in range(10):
        d.rounded_rectangle([gx0 + i * 76, gy0, gx0 + i * 76 + 62, gy0 + 22], 6, fill=GOLD if i < 6 else (52, 54, 66))
    d.text((gx0, gy0 + 34), "눈치 6/10 — 다음 장 희귀 18.2% · 실패 7.2%", font=f(FR, 25), fill=MUTED)
    y = gy0 + 86

    # 6. 연출
    y = section(y + 10, "6  한 장이 깨지는 순서")
    tw = 214
    for row, (fname, caps) in enumerate([("sequence_승급_전설.png", ["① 강림", "② 균열", "③ 승급", "④ 개화"]),
                                         ("sequence_강등_실패.png", ["① 강림", "② 금빛…?", "③ 강등", "④ 굴러떨어짐"])]):
        sheet = Image.open(ART / fname).convert("RGB")
        s = (sheet.size[0] - 12) // 2
        for i in range(4):
            tile = sheet.crop(((i % 2) * (s + 12), (i // 2) * (s + 12), (i % 2) * (s + 12) + s, (i // 2) * (s + 12) + s))
            tile = tile.crop((int(s * 0.12), int(s * 0.10), int(s * 0.88), int(s * 0.86))).resize((tw, tw), Image.LANCZOS)
            x = 80 + i * (tw + 16)
            im.paste(tile, (x, y))
            d.rectangle([x, y, x + tw, y + tw], outline=LINE, width=2)
            cw = d.textlength(caps[i], font=f(FB, 26))
            d.text((x + (tw - cw) / 2, y + tw + 8), caps[i], font=f(FB, 26), fill=TXT)
        y += tw + 54
    for r in ["빛의 색 = 등급 예고",
              "승급: 희귀 이상 + 1차 굴림값 3의 배수 (신화는 항상 두 번)",
              "강등: 실패·재앙 + 1차 굴림값 4의 배수 — 좋은 빛인 척하다 꺼진다",
              "비정상은 흰빛인 척하다가 빛이 거꾸로 빨려 들어간다"]:
        d.text((90, y), r, font=f(FR, 25), fill=MUTED)
        y += 40

    y = section(y + 18, "7  겹치면")
    for a, b in [("같은 재능 또 나옴", "각성 — 21단계에서 3단계 위로"),
                 ("비정상이 두 번", "서로 상쇄돼서 둘 다 사라지고 '정상·중'")]:
        d.text((100, y), a, font=f(FB, 30), fill=TXT)
        d.text((430, y + 2), b, font=f(FR, 28), fill=MUTED)
        y += 54

    center(H - 70, "정상 · 삼신 가챠", f(FR, 24), (110, 112, 126))
    im.save(ART / "guide_작동방식.png")
    print("saved guide_작동방식.png, last y =", y, "/", H - 100)


if __name__ == "__main__":
    main()
