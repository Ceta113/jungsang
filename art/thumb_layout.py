"""썸네일 최종 레이아웃: 세로 붓글씨 제목 + 세로 부제 + 낙관(正常) + 알에서 떨어지는 금빛 가루.

  python art/thumb_layout.py [입력] [출력]     (기본: nai/thumbnail.png → nai/thumbnail_title.png)

배치는 nai/thumbnail.png(④ 삼신의 손, seed 3765288516) 구도에 맞춘 것이다.
  - 오른쪽 위에 소매·손이 무겁게 있어 제목 덩어리를 왼쪽 위에 두어 대각으로 균형을 맞춘다.
  - 제목 아래 낙관은 '정상 판정' 도장 역할, 부제는 제목 오른쪽에 한 줄로 붙인다.
  - 금빛 가루는 깨진 알에서 아이 쪽으로만 흩뿌려 알→아이 흐름을 이어 준다.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

sys.path.insert(0, str(Path(__file__).parent))
from title_brush import GLOW, INK, composite, paste_layer, render

ROOT = Path(__file__).resolve().parent.parent
SEAL_RED = np.array([176, 44, 36], np.float32)
PAPER = np.array([243, 230, 207], np.float32)

# 구도에 맞춘 자리 (원본 832×1216 기준 비율)
TITLE = dict(text="정상", cell=0.165, cx=0.148, top=0.045)
TAGLINE = "알을 깨면 인생이 정해진다"
EGG = (0.50, 0.565)   # 깨진 알 중심
BOY = (0.50, 0.70)    # 아이 머리 위


def vertical_text(text, size, color, alpha=0.8, weight="Medium"):
    """한 글자씩 아래로 쌓은 세로 글. 띄어쓰기는 반 칸."""
    f = ImageFont.truetype("C:/Windows/Fonts/NotoSerifKR-VF.ttf", size)
    try:
        f.set_variation_by_name(weight)
    except Exception:
        pass
    step = int(size * 1.1)
    h = sum(step // 2 if c == " " else step for c in text)
    im = Image.new("L", (int(size * 1.4), h + size), 0)
    d = ImageDraw.Draw(im)
    y = 0
    for c in text:
        if c == " ":
            y += step // 2
            continue
        d.text((im.width / 2, y + size / 2), c, font=f, fill=255, anchor="mm")
        y += step
    return np.asarray(im, np.float32) / 255 * alpha, color


def seal(size, rng, text="正常"):
    """낙관: 붉은 인주 사각형에 글자를 종이색으로. 가장자리·인주 얼룩을 거칠게."""
    S = size * 4
    m = Image.new("L", (S, S), 0)
    pad = int(S * 0.06)
    ImageDraw.Draw(m).rounded_rectangle([pad, pad, S - pad, S - pad], radius=int(S * 0.06), fill=255)
    t = Image.new("L", (S, S), 0)
    f = ImageFont.truetype("C:/Windows/Fonts/batang.ttc", int(S * 0.36), index=2)
    td = ImageDraw.Draw(t)
    td.text((S / 2, S * 0.29), text[0], font=f, fill=255, anchor="mm")
    td.text((S / 2, S * 0.70), text[1], font=f, fill=255, anchor="mm")
    t = Image.fromarray((ndi.grey_dilation(np.asarray(t), size=5)))  # 획을 도장처럼 굵게
    a = np.asarray(m, np.float32) / 255
    tx = np.asarray(t, np.float32) / 255
    n = ndi.gaussian_filter(rng.standard_normal((S, S)).astype(np.float32), 6)
    n /= n.std() + 1e-6
    edge = ndi.gaussian_filter(a, 4) + 0.12 * n
    a = np.clip((edge - 0.5) * 8 + 0.5, 0, 1)
    speck = ndi.gaussian_filter(rng.standard_normal((S, S)).astype(np.float32), 2.5)
    a *= np.clip(1.25 - (speck / speck.std() > 1.6) * 1.0, 0, 1) * 0.95  # 인주가 덜 묻은 점
    out = Image.fromarray((a * 255).astype(np.uint8)).rotate(-3, resample=Image.BICUBIC).resize((size, size), Image.LANCZOS)
    txo = Image.fromarray((tx * 255).astype(np.uint8)).rotate(-3, resample=Image.BICUBIC).resize((size, size), Image.LANCZOS)
    return np.asarray(out, np.float32) / 255, np.asarray(txo, np.float32) / 255


def gold_dust(H, W, rng, n=70):
    """깨진 알에서 아이 쪽으로 떨어지는 금빛 가루(가산 합성용 밝기 맵)."""
    m = np.zeros((H, W), np.float32)
    ex, ey = EGG[0] * W, EGG[1] * H
    bx, by = BOY[0] * W, BOY[1] * H
    for _ in range(n):
        t = rng.random() ** 0.8                     # 알 가까이에 더 많이
        x = ex + (bx - ex) * t + rng.normal(0, 10 + 55 * t)
        y = ey + (by - ey) * t + rng.normal(0, 8)
        r = rng.uniform(0.8, 2.2) * (1.2 - 0.5 * t)
        b = rng.uniform(0.5, 1.0) * (1.0 - 0.6 * t)
        yi, xi = int(y), int(x)
        if 0 <= yi < H and 0 <= xi < W:
            m[yi, xi] += b * r * 6
    core = ndi.gaussian_filter(m, 1.0)
    halo = ndi.gaussian_filter(m, 5.0) * 0.8
    return core + halo


def main(src, dst):
    rng = np.random.default_rng(11)
    base = Image.open(src).convert("RGB")
    W, H = base.size
    img = np.asarray(base, np.float32)

    # 1) 제목 자리를 아주 살짝 눌러 앉힌다(왼쪽 위 비네트)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    v = np.exp(-(((xx - 0.15 * W) / (0.32 * W)) ** 2 + ((yy - 0.2 * H) / (0.26 * H)) ** 2))
    img *= (1 - 0.22 * v)[..., None]

    # 2) 금빛 가루
    dust = gold_dust(H, W, rng)
    img = img + GLOW * np.clip(dust, 0, 1.5)[..., None] * 0.9

    # 3) 제목
    cell = int(TITLE["cell"] * H)
    al, tn = render(TITLE["text"], cell, rng)
    tx0 = int(TITLE["cx"] * W - al.shape[1] / 2)
    ty0 = int(TITLE["top"] * H)
    img = composite(img, al, tn, tx0, ty0)
    rows = np.where(al.max(axis=1) > 0.3)[0]
    cols = np.where(al.max(axis=0) > 0.3)[0]
    t_top, t_bot = ty0 + rows[0], ty0 + rows[-1]
    t_left, t_right = tx0 + cols[0], tx0 + cols[-1]

    # 4) 부제: 제목 오른쪽, 제목 첫 획 높이에 맞춰. 엄지(x≈205, y≈420~)에 닿지 않게 짧게 끝낸다
    va, _ = vertical_text(TAGLINE, int(H * 0.0165), INK, alpha=0.78)
    sx0 = t_right + int(W * 0.018)
    sy0 = t_top + int(H * 0.004)
    assert sy0 + va.shape[0] - int(H * 0.0165) < 0.335 * H, "부제가 손에 닿음"
    fa = paste_layer(H, W, va, sx0, sy0)
    img = img * (1 - fa[..., None]) + INK * fa[..., None]

    # 5) 낙관: 제목 아래, 제목 오른쪽 끝에 맞춤
    s = int(H * 0.046)
    sa, st = seal(s, rng)
    px0 = t_right - s + int(W * 0.004)
    py0 = t_bot + int(H * 0.018)
    fa = paste_layer(H, W, sa, px0, py0)
    ft = paste_layer(H, W, st, px0, py0)
    col = SEAL_RED[None, None, :] * (1 - ft[..., None]) + PAPER * ft[..., None]
    img = img * (1 - fa[..., None]) + col * fa[..., None]

    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(dst)
    print(dst, f"제목 {t_left}-{t_right} x {t_top}-{t_bot}, 낙관 y {py0}-{py0 + s}")


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0] if a else ROOT / "nai/thumbnail.png", a[1] if len(a) > 1 else ROOT / "nai/thumbnail_title.png")
