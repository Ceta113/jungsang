"""삼신 가챠 연출 일러스트 렌더러 (numpy/scipy/PIL, 스트로크 페인팅 마감).

  python art/render_gacha.py            등급 5장 + 연출 4컷 시트 (1024px, 내부 2x)
  python art/render_gacha.py --quick    512px 빠른 시안
  python art/render_gacha.py --only 전설  한 장만

출력: art/out/egg_1_정상.png … egg_5_비정상.png, art/out/sequence_전설.png
"""
import math
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

QUICK = "--quick" in sys.argv
F = 1024
SS = 1 if QUICK else 2
SC = (0.5 if QUICK else 1.0) * SS
N = int(F * SC)
OUT = Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)
FONT_B = "C:/Windows/Fonts/malgunbd.ttf"
T0 = time.time()


def log(m):
    print(f"[{time.time() - T0:6.1f}s] {m}", flush=True)


_yy, _xx = np.mgrid[0:N, 0:N]
X = ((_xx + 0.5) / SC).astype(np.float32)
Y = ((_yy + 0.5) / SC).astype(np.float32)
del _yy, _xx


# ------------------------------------------------------------------ helpers
def v3(*c):
    return np.array(c, np.float32)


def sstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def lerpc(a, b, t):
    return a + (b - a) * t[..., None]


def _g(a, s):
    if a.ndim == 3:
        return np.stack([ndi.gaussian_filter(a[..., i], s, mode="nearest") for i in range(a.shape[2])], -1)
    return ndi.gaussian_filter(a, s, mode="nearest")


def _down(a, k):
    h, w = a.shape[0] // k, a.shape[1] // k
    a = a[: h * k, : w * k]
    return a.reshape(h, k, w, k, *a.shape[2:]).mean(axis=(1, 3))


def _up(a, shape):
    z = (shape[0] / a.shape[0], shape[1] / a.shape[1]) + (1,) * (a.ndim - 2)
    o = ndi.zoom(a, z, order=1, mode="nearest", grid_mode=True)[: shape[0], : shape[1]]
    ph, pw = shape[0] - o.shape[0], shape[1] - o.shape[1]
    if ph > 0 or pw > 0:
        o = np.pad(o, [(0, ph), (0, pw)] + [(0, 0)] * (a.ndim - 2), mode="edge")
    return o.astype(np.float32, copy=False)


def gblur(a, s):
    s = s * SC
    if s < 0.3:
        return a
    k = min(int(s / 3), a.shape[0] // 4, a.shape[1] // 4)
    if s <= 6 or k < 2:
        return _g(a, s)
    return _up(_g(_down(a, k), s / k), a.shape)


def vnoise(cell, seed, sx=1.0, sy=1.0):
    cxp, cyp = max(cell * sx * SC, 1.0), max(cell * sy * SC, 1.0)
    k = max(1, int(min(cxp, cyp) / 6))
    h = w = -(-N // k)
    cx, cy = cxp / k, cyp / k
    gh, gw = int(h / cy) + 4, int(w / cx) + 4
    r = np.random.default_rng(seed).random((gh, gw), dtype=np.float32)
    z = ndi.zoom(r, (cy, cx), order=3, prefilter=False, mode="nearest", grid_mode=True)[:h, :w]
    return z if k == 1 else _up(z, (N, N))


def fbm(cell, seed, octv=5, sx=1.0, sy=1.0):
    tot = np.zeros((N, N), np.float32)
    amp = nrm = 0.0
    amp = 1.0
    for o in range(octv):
        c = cell / 2 ** o
        if c * SC < 1.2:
            break
        tot += amp * vnoise(c, seed + 101 * o, sx, sy)
        nrm += amp
        amp *= 0.5
    tot /= nrm
    lo, hi = np.percentile(tot[::7, ::7], [1, 99])
    return np.clip((tot - lo) / (hi - lo + 1e-6), 0, 1)


def win(x0, y0, x1, y1):
    a, b = max(0, int(x0 * SC)), min(N, int(math.ceil(x1 * SC)))
    c, d = max(0, int(y0 * SC)), min(N, int(math.ceil(y1 * SC)))
    return slice(c, max(c, d)), slice(a, max(a, b))


def glow(buf, x, y, r, col, inten, sx=0.0, sy=0.0):
    r = max(r, 0.7 / SC)
    m = r * 3.2
    sl = win(min(x, x + sx) - m, min(y, y + sy) - m, max(x, x + sx) + m, max(y, y + sy) + m)
    if sl[0].stop <= sl[0].start or sl[1].stop <= sl[1].start:
        return
    px, py = X[sl] - x, Y[sl] - y
    L2 = sx * sx + sy * sy
    if L2 > 1e-6:
        t = np.clip((px * sx + py * sy) / L2, 0, 1)
        px, py = px - t * sx, py - t * sy
    buf[sl] += np.asarray(col, np.float32) * (np.exp(-(px * px + py * py) / (2 * r * r)) * inten)[..., None]


def lines_mask(polys, widths, blur=0.0):
    im = Image.new("L", (N, N), 0)
    d = ImageDraw.Draw(im)
    for pts, w in zip(polys, widths):
        if len(pts) > 1:
            d.line([(x * SC, y * SC) for x, y in pts], fill=255, width=max(1, int(round(w * SC))), joint="curve")
    m = np.asarray(im, np.float32) / 255.0
    return gblur(m, blur) if blur else m


def poly_mask(pts):
    im = Image.new("L", (N, N), 0)
    ImageDraw.Draw(im).polygon([(x * SC, y * SC) for x, y in pts], fill=255)
    return np.asarray(im, np.float32) / 255.0


def radial_blur(src, cx, cy, n=40, length=0.7, decay=0.96):
    k = 4 if N >= 1024 else 2
    s = _down(src, k)
    h, w = s.shape
    gy, gx = np.mgrid[0:h, 0:w].astype(np.float32)
    ccx, ccy = cx * SC / k, cy * SC / k
    acc = np.zeros_like(s)
    ws, wt = 0.0, 1.0
    for i in range(n):
        f = 1 - length * i / n
        acc += wt * ndi.map_coordinates(s, [ccy + (gy - ccy) * f, ccx + (gx - ccx) * f], order=1, mode="constant")
        ws += wt
        wt *= decay
    return _up(acc / ws, (N, N))


def stroke_paint(src, layers, seed=7):
    """Hertzmann식 스트로크 페인팅 (sRGB float 입력, 결과 sRGB float)."""
    h, w = src.shape[:2]
    rng = np.random.default_rng(seed)
    flow0 = ndi.zoom(rng.random((h // 60 + 3, w // 60 + 3)), 60, order=3)[:h, :w] * 1.6 + 0.2
    canvas = Image.fromarray((np.clip(_g(src, layers[0][0] * 0.8), 0, 1) * 255 + 0.5).astype(np.uint8))
    for R, T, maxlen, alpha in layers:
        ref = _g(src, max(R * 0.35, 0.5))
        lum = ref @ np.array([0.3, 0.55, 0.15], np.float32)
        gx = ndi.gaussian_filter(ndi.sobel(lum, 1), R * 0.6)
        gy = ndi.gaussian_filter(ndi.sobel(lum, 0), R * 0.6)
        gmax = np.percentile(np.hypot(gx, gy), 60) * 0.25 + 1e-6
        cur = np.asarray(canvas, np.float32) / 255.0
        diff = np.sqrt(((cur - ref) ** 2).sum(-1))
        hb, wb = h // R, w // R
        blk = diff[: hb * R, : wb * R].reshape(hb, R, wb, R).transpose(0, 2, 1, 3).reshape(hb, wb, R * R)
        bmean, barg = blk.mean(-1), blk.argmax(-1)
        draw = ImageDraw.Draw(canvas, "RGBA")
        cells = np.argwhere(bmean > T)
        rng.shuffle(cells)
        wdt = max(1, int(round(R * 1.15)))
        r_ = wdt / 2
        for by, bx in cells:
            a_ = barg[by, bx]
            y, x = by * R + a_ // R, bx * R + a_ % R
            c = ref[y, x]
            pts = [(x + 0.5, y + 0.5)]
            px_, py_ = float(x), float(y)
            ldx = ldy = 0.0
            for k in range(maxlen):
                ix_, iy_ = int(px_), int(py_)
                if k > 0:
                    if not (0 <= ix_ < w and 0 <= iy_ < h):
                        break
                    rc = ref[iy_, ix_]
                    if k >= 2 and np.abs(rc - c).sum() > np.abs(rc - cur[iy_, ix_]).sum():
                        break
                    pts.append((px_ + 0.5, py_ + 0.5))
                g_x, g_y = gx[iy_, ix_], gy[iy_, ix_]
                gm = math.hypot(g_x, g_y)
                if gm > gmax:
                    dx, dy = -g_y / gm, g_x / gm
                else:
                    th = flow0[iy_, ix_]
                    dx, dy = math.cos(th), math.sin(th)
                if dx * ldx + dy * ldy < 0:
                    dx, dy = -dx, -dy
                if k > 0:
                    dx, dy = 0.6 * dx + 0.4 * ldx, 0.6 * dy + 0.4 * ldy
                    n_ = math.hypot(dx, dy) + 1e-9
                    dx, dy = dx / n_, dy / n_
                px_ += dx * R * 0.9
                py_ += dy * R * 0.9
                ldx, ldy = dx, dy
            col = tuple(int(v * 255 + 0.5) for v in np.clip(c, 0, 1)) + (alpha,)
            if len(pts) > 1:
                draw.line(pts, fill=col, width=wdt, joint="curve")
            for qx, qy in (pts[0], pts[-1]):
                draw.ellipse([qx - r_, qy - r_, qx + r_, qy + r_], fill=col)
    return np.asarray(canvas, np.float32) / 255.0


# ------------------------------------------------------------------ tiers
TIERS = {
    "정상": dict(no=1, col=v3(1.00, 0.93, 0.82), stars="★", crack=1, inten=0.9, parts=24),
    "준수": dict(no=2, col=v3(0.28, 0.62, 1.00), stars="★★", crack=2, inten=1.5, parts=60),
    "희귀": dict(no=3, col=v3(0.66, 0.34, 1.00), stars="★★★", crack=3, inten=2.0, parts=90),
    "전설": dict(no=4, col=v3(1.00, 0.70, 0.24), stars="★★★★", crack=4, inten=3.0, parts=170),
    "비정상": dict(no=5, col=v3(1.00, 1.00, 1.00), stars="??", crack=2, inten=2.2, parts=60),
}
EGG = dict(cx=512.0, cy=425.0, a=150.0, b=200.0, rot=math.radians(-7))
HOR = 700.0


def egg_fields(cx, cy, a, b, rot):
    c, s = math.cos(rot), math.sin(rot)
    dx, dy = X - cx, Y - cy
    lx = dx * c + dy * s
    ly = -dx * s + dy * c
    t = np.clip(ly / b, -1.2, 1.2)
    w = a * np.sqrt(np.clip(1 - t * t, 0, 1)) * (1 + 0.13 * t)
    aa = np.clip((w - np.abs(lx)) * SC / 0.9 + 0.5, 0, 1) * np.clip((1 - np.abs(ly / b)) * b * SC / 0.9 + 0.5, 0, 1)
    px = np.clip(lx / np.maximum(w, 1e-3), -1, 1)
    tt = np.clip(t, -1, 1)
    nxl = px * np.sqrt(1 - tt * tt)
    nyl = tt
    nzl = np.sqrt(np.clip(1 - nxl * nxl - nyl * nyl, 0, 1))
    nx = nxl * c - nyl * s
    ny = nxl * s + nyl * c
    return aa, nx, ny, nzl, lx, ly


def to_frame(cx, cy, rot, lx, ly):
    c, s = math.cos(rot), math.sin(rot)
    return cx + lx * c - ly * s, cy + lx * s + ly * c


def inside_egg(lx, ly, a, b, margin=6):
    t = ly / b
    if abs(t) >= 0.97:
        return False
    w = a * math.sqrt(1 - t * t) * (1 + 0.13 * t)
    return abs(lx) < w - margin


def make_cracks(seed, level, eg):
    rng = np.random.default_rng(seed)
    a, b = eg["a"], eg["b"]
    polys, widths = [], []

    def walk(lx, ly, ang, steps, wdt, depth):
        pts = [to_frame(eg["cx"], eg["cy"], eg["rot"], lx, ly)]
        for _ in range(steps):
            ang += rng.normal(0, 0.55 if level > 1 else 0.28)
            st = rng.uniform(7, 15)
            nlx, nly = lx + math.cos(ang) * st, ly + math.sin(ang) * st
            if not inside_egg(nlx, nly, a, b):
                break
            lx, ly = nlx, nly
            pts.append(to_frame(eg["cx"], eg["cy"], eg["rot"], lx, ly))
            if depth < 2 and rng.random() < 0.16:
                walk(lx, ly, ang + rng.choice([-1, 1]) * rng.uniform(0.6, 1.3), int(steps * 0.45), wdt * 0.6, depth + 1)
        polys.append(pts)
        widths.append(wdt)

    n_main = {1: 1, 2: 3, 3: 5, 4: 7}[level]
    for i in range(n_main):
        lx0 = rng.uniform(-0.45, 0.45) * a
        ly0 = rng.uniform(-0.55, 0.15) * b
        walk(lx0, ly0, rng.uniform(0, 2 * math.pi), int(rng.uniform(9, 18) + level * 3), 3.2 if level > 1 else 2.6, 0)
        walk(lx0, ly0, rng.uniform(0, 2 * math.pi), int(rng.uniform(6, 12) + level * 2), 2.6, 0)
    return polys, widths


def zig(lx, a):
    return -0.12 * EGG["b"] + 13 * np.abs(((lx / 34.0) % 1.0) * 2 - 1) - 6.5


# ------------------------------------------------------------------ scene
def background(tier, seed, inverted=False):
    t = Y / F
    col = TIERS[tier]["col"]
    d = np.hypot(X - EGG["cx"], Y - EGG["cy"])
    if not inverted:
        img = lerpc(v3(0.008, 0.010, 0.020), v3(0.020, 0.024, 0.040), sstep(0.0, 0.75, t))
        img += col * (np.exp(-d / 360) * 0.06 + np.exp(-d / 170) * 0.05)[..., None]
        cl = fbm(230, seed, 5, sx=2.6)
        m = sstep(0.48, 0.82, cl) * (0.35 + 0.65 * sstep(0.1, 0.65, t))
        img = lerpc(img, v3(0.030, 0.033, 0.050) + col * 0.025, m * 0.7)
        cl2 = fbm(90, seed + 7, 4, sx=3.0)
        img += v3(0.02, 0.022, 0.03) * (sstep(0.55, 0.9, cl2) * 0.6)[..., None]
    else:
        img = lerpc(v3(0.62, 0.60, 0.56), v3(0.44, 0.43, 0.42), sstep(0.0, 0.75, t))
        cl = fbm(230, seed, 5, sx=2.6)
        img = lerpc(img, v3(0.74, 0.72, 0.68), sstep(0.5, 0.85, cl) * 0.6)
        img *= (1 - 0.55 * np.exp(-d / 240))[..., None]          # 빛이 알 쪽으로 빨려 들어간 자리
    return img


def shell_color(nx, ny, nz, dark=False):
    L = np.array([-0.45, -0.70, 0.55], np.float32)
    L /= np.linalg.norm(L)
    H = L + np.array([0, 0, 1], np.float32)
    H /= np.linalg.norm(H)
    ndl = nx * L[0] + ny * L[1] + nz * L[2]
    wrap = np.clip((ndl + 0.35) / 1.35, 0, 1)
    sp = np.clip(nx * H[0] + ny * H[1] + nz * H[2], 0, 1)
    amb = 0.55 + 0.45 * np.clip(-ny, -1, 1)
    if dark:
        base = v3(0.012, 0.012, 0.014)
        return (base * (amb * 0.6 + wrap * 0.8)[..., None]
                + v3(1, 1, 1) * (sp ** 90 * 1.4 + sp ** 14 * 0.06)[..., None])
    base = v3(0.62, 0.58, 0.52)
    return (base * (amb * 0.22 + wrap * 0.55)[..., None]
            + v3(0.9, 0.92, 1.0) * (sp ** 40 * 0.30)[..., None])


def render(tier, seed=1, phase="final", crack_col=None, egg_cy=None, flash=0.0, shake=0.0, descend=False):
    """phase: final(등급 결과) / closed(금 없음) / crack(금+빛) / open(깨짐)"""
    P = TIERS[tier]
    col = P["col"] if crack_col is None else crack_col
    inv = tier == "비정상" and phase == "final"
    eg = dict(EGG)
    if egg_cy is not None:
        eg["cy"] = egg_cy
    opened = (phase == "final" and tier == "전설") or phase == "open"
    level = P["crack"] if phase in ("final", "crack", "open") else 0
    rng = np.random.default_rng(seed + 10 * P["no"])

    img = background(tier, 30 + seed, inv)
    emi = np.zeros((N, N, 3), np.float32)

    def egg_layer(open_, level_, dark):
        lay = np.zeros((N, N, 3), np.float32)
        al = np.zeros((N, N), np.float32)
        e = np.zeros((N, N, 3), np.float32)
        aa, nx, ny, nz, lx, ly = egg_fields(eg["cx"], eg["cy"], eg["a"], eg["b"], eg["rot"])
        speck = fbm(6, 5 + seed, 3)
        sc_ = shell_color(nx, ny, nz, dark) * (0.92 + 0.16 * speck)[..., None]
        if open_:
            zz = zig(lx, eg["a"])
            bottom = aa * np.clip((ly - zz) * SC / 0.9 + 0.5, 0, 1)
            lay += sc_ * bottom[..., None]
            al = np.maximum(al, bottom)
            rim = bottom * np.exp(-np.maximum(ly - zz, 0) / 10.0)
            e += col * (rim * P["inten"] * 1.6)[..., None]
            capc = to_frame(eg["cx"], eg["cy"], eg["rot"], 0, -0.6 * eg["b"])
            dxc, dyc, drot = 34.0, -150.0, math.radians(22)
            aa2, nx2, ny2, nz2, lx2, ly2 = egg_fields(eg["cx"] + dxc, eg["cy"] + dyc, eg["a"], eg["b"], eg["rot"] + drot)
            cap = aa2 * np.clip((zig(lx2, eg["a"]) - ly2) * SC / 0.9 + 0.5, 0, 1)
            cc = shell_color(nx2, ny2, nz2, dark) * (0.92 + 0.16 * speck)[..., None]
            caprim = cap * np.exp(-np.maximum(zig(lx2, eg["a"]) - ly2, 0) / 9.0)
            cc += col * (caprim * 0.9)[..., None]
            lay = lay * (1 - cap[..., None]) + cc * cap[..., None]
            al = cap + al * (1 - cap)
            e = e * (1 - cap[..., None]) + col * (caprim * P["inten"] * 0.8)[..., None]
            core = to_frame(eg["cx"], eg["cy"], eg["rot"], 0, -0.12 * eg["b"] - 30)
            for r_, i_ in ((34, 3.0), (90, 0.8), (220, 0.18)):
                glow(e, core[0], core[1], r_, col * 0.7 + 0.3, i_)
            del aa2, nx2, ny2, nz2, lx2, ly2
        else:
            lay += sc_ * aa[..., None]
            al = aa.copy()
        if level_ > 0:
            polys, widths = make_cracks(seed + 3 * P["no"], level_, eg)
            cm = lines_mask(polys, widths) * aa
            thin = lines_mask(polys, [w * 0.45 for w in widths]) * aa
            sss = gblur(cm, 16) * aa
            lay += col * (sss * 0.25 * P["inten"])[..., None] * al[..., None]
            lay *= (1 - cm * 0.85)[..., None]
            e += (col * cm[..., None] * 1.6 + thin[..., None] * 2.2) * (P["inten"] * 0.8)
            e += col * (gblur(cm, 5) * 1.2 + gblur(cm, 18) * 0.8)[..., None] * P["inten"] * 0.6
        return lay, al, e, aa

    dark = tier == "비정상"
    lay, al, e, aa = egg_layer(opened, level, dark)

    # 강림: 위에서 내려오는 빛 줄기 + 세로 잔상
    if descend:
        trail = (np.exp(-((X - eg["cx"]) / 70) ** 2) * sstep(-50, eg["cy"] - 60, Y)
                 * (1 - sstep(eg["cy"] - 60, eg["cy"], Y)))
        emi += col * (trail * 0.25)[..., None]
        lay = ndi.uniform_filter1d(lay, int(26 * SC), axis=0, origin=int(9 * SC))
        al = ndi.uniform_filter1d(al, int(26 * SC), axis=0, origin=int(9 * SC))
    if shake > 0:
        k_ = max(1, int(shake * SC))
        lay = ndi.uniform_filter1d(lay, k_, axis=1)
        al = ndi.uniform_filter1d(al, k_, axis=1)
        e = ndi.uniform_filter1d(e, k_, axis=1)

    # 안쪽에서 비치는 빛이 알 뒤쪽 가장자리를 감싼다
    bl = gblur(al, 3.0)
    edge_back = np.clip(bl - al, 0, 1) * 3.0
    emi += col * (edge_back * (0.35 + 0.15 * level))[..., None]

    img = img * (1 - al[..., None]) + lay
    emi = emi * (1 - al[..., None]) + e

    # 번개 (희귀), 광선 (전설), 수렴하는 빛줄기 (비정상)
    if tier == "희귀" and phase == "final":
        arcs = []
        for i in range(7):
            ang = rng.uniform(0, 2 * math.pi)
            r0 = 160
            x, y = eg["cx"] + math.cos(ang) * r0 * 0.9, eg["cy"] + math.sin(ang) * r0 * 1.2
            pts = [(x, y)]
            for _ in range(int(rng.uniform(5, 11))):
                ang += rng.normal(0, 0.5)
                x += math.cos(ang) * rng.uniform(12, 22)
                y += math.sin(ang) * rng.uniform(12, 22)
                pts.append((x, y))
            arcs.append(pts)
        am = lines_mask(arcs, [1.6] * len(arcs))
        emi += col * (am * 2.2 + gblur(am, 6) * 1.2)[..., None] + (am * 1.5)[..., None]
    if opened:
        src = np.clip(emi.mean(-1) - 1.0, 0, 2.0) * (1 - al)
        core = to_frame(eg["cx"], eg["cy"], eg["rot"], 0, -0.12 * eg["b"] - 30)
        rays = radial_blur(src, core[0], core[1], 48, 0.85, 0.965)
        ang_ = np.arctan2(Y - core[1], X - core[0])
        streak = 0.55 + 0.45 * np.cos(ang_ * 9 + 0.7) ** 8 + 0.3 * np.cos(ang_ * 5 + 2.1) ** 12
        emi += col * (rays * 0.55 * streak)[..., None]
        img = lerpc(img, img + col * 0.02, sstep(HOR + 50, 0, Y) * 0.6)
    if inv:
        # 빛이 밖으로 퍼지지 않고 알 쪽으로 빨려 들어가는 어두운 줄기
        dk = np.zeros((N, N, 3), np.float32)
        for i in range(80):
            ang = rng.uniform(0, 2 * math.pi)
            r1 = rng.uniform(230, 560)
            x, y = eg["cx"] + math.cos(ang) * r1, eg["cy"] + math.sin(ang) * r1 * 0.9
            L_ = rng.uniform(50, 140)
            glow(dk, x, y, rng.uniform(0.9, 1.8), v3(1, 1, 1), rng.uniform(0.4, 0.9),
                 -math.cos(ang) * L_, -math.sin(ang) * L_)
        img *= (1 - np.clip(dk[..., 0], 0, 0.85))[..., None]
        # 크랙에서 색수차: 빨강·파랑이 양옆으로 갈라진다
        sh = int(4 * SC)
        emi = np.stack([np.roll(emi[..., 0], sh, 1), emi[..., 1], np.roll(emi[..., 2], -sh, 1)], -1)

    # 파편
    if opened or (tier in ("희귀", "비정상") and phase == "final"):
        nsh = 26 if opened else 14
        for i in range(nsh):
            ang = rng.uniform(-math.pi, 0.15) if opened else rng.uniform(0, 2 * math.pi)
            rr = rng.uniform(190, 400) if opened else rng.uniform(210, 290)
            x = eg["cx"] + math.cos(ang) * rr
            y = eg["cy"] - 40 + math.sin(ang) * rr * (0.9 if opened else 0.75)
            s_ = rng.uniform(8, 22)
            rot = rng.uniform(0, 2 * math.pi)
            pts = [(x + math.cos(rot + k * 2.1 + rng.normal(0, 0.3)) * s_, y + math.sin(rot + k * 2.1 + rng.normal(0, 0.3)) * s_)
                   for k in range(3)]
            pm = poly_mask(pts)
            shade = rng.uniform(0.04, 0.12) if not dark else 0.01
            fc = v3(0.50, 0.47, 0.42) * shade * 3 if not dark else v3(0.01, 0.01, 0.012)
            img = img * (1 - pm[..., None]) + fc * pm[..., None]
            ed = np.clip(gblur(pm, 1.2) - pm * 0.6, 0, 1)
            emi = emi * (1 - pm[..., None]) + col * (ed * 0.9)[..., None]

    # 입자
    for i in range(0 if inv else (P["parts"] if phase == "final" else P["parts"] // 3)):
        ang = rng.uniform(0, 2 * math.pi)
        rr = rng.uniform(170, 470) ** 1.0
        x = eg["cx"] + math.cos(ang) * rr
        y = eg["cy"] + math.sin(ang) * rr * 0.85 - rng.uniform(0, 80)
        if y > HOR - 5:
            continue
        sz = rng.uniform(0.8, 2.2)
        it = rng.uniform(0.3, 1.6) * (1.6 if opened else 1.0)
        vy = -rng.uniform(4, 16) if not inv else 0
        glow(emi, x, y, sz, col if not inv else v3(1, 1, 1), it * (1 if not inv else 0.0), 0, vy)

    # 수면: 위 장면을 뒤집어 비춘다 (비정상은 '열린 알'이 비친다)
    refl_src = img + emi
    if inv:
        # 물에는 멀쩡한 흰 알이 비친다 — 겉으로는 '정상'인 척
        lay2, al2, e2, _ = egg_layer(False, 0, False)
        refl_src = background(tier, 30 + seed, True) * 0.45 * (1 - al2[..., None]) + lay2 * 3.2
    yy = (2 * HOR - Y)
    rip = (fbm(40, 77 + seed, 3, sx=3.0, sy=0.4) - 0.5) * 10
    sy_ = np.clip(yy * SC, 0, N - 1)
    sx_ = np.clip((X + rip) * SC, 0, N - 1)
    refl = np.stack([ndi.map_coordinates(refl_src[..., c], [sy_, sx_], order=1) for c in range(3)], -1)
    refl = gblur(refl, 2.5)
    water = sstep(HOR - 1, HOR + 1, Y)
    wcol = v3(0.006, 0.008, 0.014) if not inv else v3(0.012, 0.012, 0.014)
    depth = sstep(HOR, F, Y)
    refl_k = (0.55 - 0.25 * depth) if not inv else (0.75 - 0.2 * depth)
    img = lerpc(img, wcol + refl * refl_k[..., None], water)
    emi *= (1 - water)[..., None]
    # 물 위 동심원 (준수 이상)
    if P["no"] >= 2 and phase == "final":
        ry_ = HOR + 40
        rr_ = np.hypot((X - eg["cx"]) / 3.2, (Y - ry_))
        for R_ in (30, 52, 78):
            ring = np.exp(-((rr_ - R_) / 1.6) ** 2) * water
            emi += col * (ring * 0.5 * (90 - R_) / 60)[..., None]
    if flash > 0:
        glow(emi, eg["cx"], eg["cy"], 220, v3(1, 0.95, 0.85), flash)
    return img, emi, al, aa


def finish(img, emi, egg_a, tier, label=True, out_name=None, paint=True, extra_text=None):
    col = TIERS[tier]["col"]
    img = img + emi
    br = np.maximum(img - 0.9, 0) * 0.6 + np.maximum(emi, 0) * 0.5
    img = img + gblur(br, 3) * 0.45 + gblur(br, 14) * 0.35 + gblur(br, 50) * 0.3
    if SS > 1:
        img = _down(img, SS)
        egg_a = _down(egg_a, SS)
        emif = _down(emi, SS)
    else:
        emif = emi
    x = np.maximum(img, 0)
    tm = np.clip((x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14), 0, 1)
    srgb = np.where(tm <= 0.0031308, tm * 12.92, 1.055 * np.power(tm, 1 / 2.4) - 0.055).astype(np.float32)
    srgb = np.clip(srgb + 0.5 * (srgb - 0.42) * srgb * (1 - srgb), 0, 1)
    h = srgb.shape[0]
    if paint:
        s_ = h / 1024
        lay = [(max(2, int(16 * s_)), 0.05, 7, 235), (max(2, int(8 * s_)), 0.045, 9, 225),
               (max(1, int(4 * s_ + 0.5)), 0.04, 10, 215)]
        pt = stroke_paint(srgb, lay, seed=TIERS[tier]["no"])
        focal = np.clip(emif.max(-1) * 0.6, 0, 1)
        k = 0.85 * (1 - egg_a) + 0.6 * egg_a
        k = k * (1 - 0.55 * ndi.gaussian_filter(focal, 2 * s_))
        srgb = lerpc(srgb, pt, k)
    fy, fx = np.mgrid[0:h, 0:h].astype(np.float32) / h
    vig = 1 - 0.35 * np.clip(((fx - 0.5) * 1.5) ** 2 + ((fy - 0.47) * 1.4) ** 2, 0, 1.5) ** 1.3
    srgb *= vig[..., None]
    if label:
        srgb *= (1 - 0.5 * sstep(0.84, 0.97, fy))[..., None]
    srgb += (np.random.default_rng(5).normal(0, 1, (h, h)).astype(np.float32) * 0.008)[..., None]
    im = Image.fromarray((np.clip(srgb, 0, 1) * 255 + 0.5).astype(np.uint8))
    if label:
        d = ImageDraw.Draw(im)
        s_ = h / 1024
        f1 = ImageFont.truetype(FONT_B, int(46 * s_))
        f2 = ImageFont.truetype(FONT_B, int(30 * s_))
        name = f"【{tier}】"
        stars = TIERS[tier]["stars"]
        c8 = tuple(int(v) for v in np.clip(col * 255, 0, 255)) if tier != "비정상" else (236, 234, 228)
        tw = d.textlength(name, font=f1)
        sw = d.textlength(stars, font=f2)
        y0 = int(918 * s_)
        d.text(((h - tw) / 2, y0), name, font=f1, fill=c8)
        d.text(((h - sw) / 2, y0 + int(56 * s_)), stars, font=f2, fill=c8)
    if extra_text:
        d = ImageDraw.Draw(im)
        s_ = h / 1024
        f = ImageFont.truetype(FONT_B, int(40 * s_))
        d.text((int(36 * s_), int(30 * s_)), extra_text, font=f, fill=(235, 232, 225))
    if out_name:
        im.save(OUT / out_name)
        log(f"saved {out_name}")
    return im


def main():
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1]
    for tier, P in TIERS.items():
        if only and tier != only:
            continue
        log(f"render {tier}")
        img, emi, al, aa = render(tier)
        finish(img, emi, al, tier, out_name=f"egg_{P['no']}_{tier}.png")
    if only and only != "sequence":
        return
    log("sequence")
    blue, gold = TIERS["준수"]["col"], TIERS["전설"]["col"]
    frames = [
        ("① 강림", render("전설", phase="closed", crack_col=blue, egg_cy=300, descend=True)),
        ("② 균열 · 파란빛", render("전설", phase="crack", crack_col=blue)),
        ("③ 승급 · 빛이 바뀐다", render("전설", phase="crack", crack_col=blue * 0.35 + gold * 0.65, flash=0.15, shake=14)),
        ("④ 개화 · 【전설】", render("전설", phase="final")),
    ]
    tiles = []
    for cap, (img, emi, al, aa) in frames:
        tiles.append(finish(img, emi, al, "전설", label=False, extra_text=cap))
    s = tiles[0].size[0]
    sheet = Image.new("RGB", (s * 2 + 12, s * 2 + 12), (8, 9, 12))
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % 2) * (s + 12), (i // 2) * (s + 12)))
    sheet.save(OUT / "sequence_전설.png")
    log("saved sequence_전설.png")


if __name__ == "__main__":
    main()
