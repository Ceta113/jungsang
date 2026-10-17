"""웹 실행기(web/index.html)의 캔버스 연출용 붓터치 재료.

  python art/render_web_assets.py

출력 (web/img/):
  bg_dark/dull/blood/dawn/pale.webp   배경 + 수면 반사 (알 없음, 1024x1024)
  egg_normal/dull/burnt/dark.webp     알 껍데기 (투명 배경, 360x460, 알 중심이 이미지 중심)
  tex.webp                            붓결 질감 (512x512, 소프트 라이트로 덮어 씀)
알의 모양·위치·수평선은 render_gacha.py의 EGG·HOR과 같다. 캔버스는 이 좌표계를 그대로 쓴다.
"""
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

import render_gacha as R

WEB = Path(__file__).parent.parent / "web" / "img"
WEB.mkdir(parents=True, exist_ok=True)


def bg_with_water(kind, col):
    sp = dict(bg=kind, col=col)
    img = R.background(sp, 41)
    rip = (R.fbm(40, 77, 3, sx=3.0, sy=0.4) - 0.5) * 10
    sy_ = np.clip((2 * R.HOR - R.Y) * R.SC, 0, R.N - 1)
    sx_ = np.clip((R.X + rip) * R.SC, 0, R.N - 1)
    refl = R.gblur(np.stack([ndi.map_coordinates(img[..., c], [sy_, sx_], order=1) for c in range(3)], -1), 2.5)
    water = R.sstep(R.HOR - 1, R.HOR + 1, R.Y)
    depth = R.sstep(R.HOR, R.F, R.Y)
    inv = kind == "pale"
    wcol = R.v3(0.012, 0.012, 0.014) if inv else R.v3(0.006, 0.008, 0.014)
    k = (0.75 - 0.2 * depth) if inv else (0.55 - 0.25 * depth)
    return R.lerpc(img, wcol + refl * k[..., None], water)


def main():
    zero = np.zeros((R.N, R.N), np.float32)
    zero3 = np.zeros((R.N, R.N, 3), np.float32)
    spec = R.spec("정상", 1)
    for kind, col in (("dark", R.v3(0.55, 0.58, 0.68)), ("dull", R.FAMS["실패"]["col"]),
                      ("blood", R.FAMS["재앙"]["col"]), ("dawn", R.FAMS["신화"]["col"]), ("pale", R.v3(1, 1, 1))):
        im = R.finish(bg_with_water(kind, col), zero3, zero, dict(spec, step=1), label=False)
        im.save(WEB / f"bg_{kind}.webp", quality=84, method=6)
        R.log(f"bg_{kind}")

    # 알 껍데기: 화면 중앙에 회전 없이 그리고, 붓터치로 칠한 뒤 알 모양으로 오려 낸다
    cx = cy = 512.0
    for kind in ("normal", "dull", "burnt", "dark"):
        aa, nx, ny, nz, lx, ly = R.egg_fields(cx, cy, R.EGG["a"], R.EGG["b"], 0.0)
        speck = R.fbm(6, 5, 3)
        shell = R.shell_color(nx, ny, nz, kind) * (0.92 + 0.16 * speck)[..., None]
        base = R.v3(0.03, 0.03, 0.035) if kind != "dark" else R.v3(0.4, 0.4, 0.4)
        img = base * (1 - aa[..., None]) + shell * aa[..., None]
        im = R.finish(img, zero3, aa, dict(spec, step=8), label=False)
        im = im.convert("RGBA")
        a_ = R._down(aa, R.SS) if R.SS > 1 else aa
        a_ = ndi.binary_erosion(a_ > 0.5, iterations=1).astype(np.float32)
        a_ = ndi.gaussian_filter(a_, 0.8)
        alpha = Image.fromarray((np.clip(a_, 0, 1) * 255).astype(np.uint8))
        im.putalpha(alpha)
        box = (int(cx - 180), int(cy - 230), int(cx + 180), int(cy + 230))
        im.crop(box).save(WEB / f"egg_{kind}.webp", quality=88, method=6)
        R.log(f"egg_{kind}")

    # 붓결 질감 (회색, 평균 0.5)
    rng = np.random.default_rng(9)
    n = ndi.zoom(rng.random((40, 40)), 13, order=3)[:512, :512]
    n2 = ndi.zoom(rng.random((130, 130)), 4, order=3)[:512, :512]
    src = np.clip(0.5 + (n - 0.5) * 0.5 + (n2 - 0.5) * 0.35, 0, 1).astype(np.float32)
    src = np.stack([src] * 3, -1)
    pt = R.stroke_paint(src, [(14, 0.01, 8, 235), (6, 0.008, 10, 220), (3, 0.006, 10, 210)], seed=21)
    g = pt.mean(-1)
    g = 0.5 + (g - g.mean()) * 1.6
    Image.fromarray((np.clip(g, 0, 1) * 255).astype(np.uint8)).save(WEB / "tex.webp", quality=80, method=6)
    R.log("tex")


if __name__ == "__main__":
    main()
