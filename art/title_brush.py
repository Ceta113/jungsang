"""세로 붓글씨 제목 얹기 — 궁서 글리프에 마른 붓(비백) 결을 입혀 그림 위에 합성한다.

  python art/title_brush.py 입력.png 출력.png [--text 정상] [--cx 0.84] [--top 0.33] [--size 0.25]

cx: 글자 열 중심의 가로 위치(0~1), top: 첫 글자 윗변(0~1), size: 글자 한 칸 높이(이미지 높이 대비).
붓 결은 글자 모양에서 획 방향을 추정(구조 텐서)해 그 방향으로 노이즈를 끌어 만든다(LIC).
"""
import argparse

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

FONT = ("C:/Windows/Fonts/batang.ttc", 2)  # 궁서
INK = np.array([246, 238, 220], np.float32)   # 따뜻한 미색
GLOW = np.array([239, 205, 140], np.float32)  # 사이트 금빛
SS = 2  # 슈퍼샘플


def fbm(shape, rng, scales=(64, 24, 8), weights=(0.55, 0.3, 0.15)):
    out = np.zeros(shape, np.float32)
    for s, w in zip(scales, weights):
        n = ndi.gaussian_filter(rng.standard_normal(shape).astype(np.float32), s)
        out += w * n / (n.std() + 1e-6)
    return out


def glyph_mask(text, cell, rng):
    """세로로 쌓은 글자 마스크. 글자마다 살짝 기울기·크기를 흔들어 손글씨 맛을 낸다."""
    f = ImageFont.truetype(FONT[0], int(cell * 0.92), index=FONT[1])
    gap = 1.12  # 궁서는 받침이 아래로 길게 떨어져서, 글자 사이를 넉넉히 둬야 '정'과 '상'이 한 덩어리씩 읽힌다
    h = int(cell * (len(text) - 1) * gap + cell * 1.3)
    m = Image.new("L", (int(cell * 1.3), h), 0)
    for i, ch in enumerate(text):
        g = Image.new("L", (int(cell * 1.3), int(cell * 1.3)), 0)
        ImageDraw.Draw(g).text((cell * 0.65, cell * 0.65), ch, font=f, fill=255, anchor="mm")
        g = g.rotate(rng.uniform(-3, 3), resample=Image.BICUBIC)
        sc = rng.uniform(0.98, 1.03)
        g = g.resize((int(g.width * sc), int(g.height * sc)), Image.LANCZOS)
        x = (m.width - g.width) // 2 + int(rng.uniform(-0.03, 0.03) * cell)
        m.paste(g, (x, int(i * cell * gap)), g)
    a = np.asarray(m, np.float32) / 255
    # 붓 굵기: 궁서 획이 가늘어서 흐린 뒤 낮은 문턱으로 다시 잘라 살을 붙인다
    a = ndi.gaussian_filter(a, cell * 0.016)
    return np.clip((a - 0.3) * 9, 0, 1)


def brush(mask, rng):
    shape = mask.shape
    # 1) 가장자리를 거칠게: 살짝 흐린 마스크에 노이즈를 더해 다시 자른다
    rough = ndi.gaussian_filter(mask, 1.6 * SS) + 0.16 * fbm(shape, rng, (12 * SS, 4 * SS, 1.5 * SS))
    solid = np.clip((rough - 0.5) * 6 + 0.5, 0, 1)

    # 2) 획 방향: 구조 텐서의 주 고유벡터에 수직
    ms = ndi.gaussian_filter(mask, 5 * SS)
    gy, gx = np.gradient(ms)
    jxx, jyy, jxy = (ndi.gaussian_filter(a, 7 * SS) for a in (gx * gx, gy * gy, gx * gy))
    theta = 0.5 * np.arctan2(2 * jxy, jxx - jyy) + np.pi / 2
    dx, dy = np.cos(theta), np.sin(theta)

    # 3) LIC: 흰 노이즈를 획 방향으로 끌어 붓털 결
    noise = rng.random(shape).astype(np.float32)
    yy, xx = np.mgrid[0:shape[0], 0:shape[1]].astype(np.float32)
    acc = np.zeros(shape, np.float32)
    steps = 14
    for k in range(-steps, steps + 1):
        t = k * 1.6 * SS
        acc += ndi.map_coordinates(noise, [yy + dy * t, xx + dx * t], order=1, mode="reflect")
    lic = acc / (2 * steps + 1)
    lic = (lic - ndi.gaussian_filter(lic, 6 * SS))
    lic = (lic - lic.mean()) / (lic.std() + 1e-6)

    # 4) 마른 붓: 획 가장자리와 군데군데 얼룩진 구역에서만 결 사이가 비게
    dist = ndi.distance_transform_edt(solid > 0.5)
    band = np.clip(1 - dist / (9 * SS), 0, 1)
    patch = np.clip(fbm(shape, rng, (50 * SS, 20 * SS), (0.7, 0.3)) * 0.9 + 0.05, 0, 1)
    dryness = np.clip(band * 0.85 + patch * 0.7, 0, 1)
    gaps = np.clip((lic - 0.25) * 1.8, 0, 1)
    alpha = solid * (1 - gaps * dryness)
    tone = 0.9 + 0.1 * np.clip(fbm(shape, rng, (30 * SS, 8 * SS)), -1, 1)  # 먹 농담
    return np.clip(alpha, 0, 1), tone


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("dst")
    ap.add_argument("--text", default="정상")
    ap.add_argument("--cx", type=float, default=0.84)
    ap.add_argument("--top", type=float, default=0.33)
    ap.add_argument("--size", type=float, default=0.25)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)

    base = Image.open(a.src).convert("RGB")
    W, H = base.size
    cell = int(a.size * H * SS)
    mask = glyph_mask(a.text, cell, rng)
    alpha, tone = brush(mask, rng)

    # 원래 크기로 내리기
    sm = (int(mask.shape[1] / SS), int(mask.shape[0] / SS))
    al = np.asarray(Image.fromarray((alpha * 255).astype(np.uint8)).resize(sm, Image.LANCZOS), np.float32) / 255
    tn = np.asarray(Image.fromarray((tone * 200).astype(np.uint8)).resize(sm, Image.BILINEAR), np.float32) / 200

    x0 = int(a.cx * W - sm[0] / 2)
    y0 = int(a.top * H)
    full_a = np.zeros((H, W), np.float32)
    full_t = np.ones((H, W), np.float32)
    ys, xs = slice(max(y0, 0), min(y0 + sm[1], H)), slice(max(x0, 0), min(x0 + sm[0], W))
    full_a[ys, xs] = al[ys.start - y0:ys.stop - y0, xs.start - x0:xs.stop - x0]
    full_t[ys, xs] = tn[ys.start - y0:ys.stop - y0, xs.start - x0:xs.stop - x0]

    img = np.asarray(base, np.float32)
    # 은은한 금빛 번짐(글자 뒤) → 글자
    glow = ndi.gaussian_filter(full_a, 14)[..., None] * 0.55
    img = img + (GLOW - img) * np.clip(glow * 0.6, 0, 1) * 0.5 + GLOW * glow * 0.12
    ink = INK * full_t[..., None]
    img = img * (1 - full_a[..., None]) + ink * full_a[..., None]
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(a.dst)
    print(a.dst)


if __name__ == "__main__":
    main()
