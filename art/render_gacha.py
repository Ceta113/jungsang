"""삼신 가챠 연출 일러스트 렌더러 (numpy/scipy/PIL, 스트로크 페인팅 마감).

  python art/render_gacha.py              24단계 전부 + 연출 시트 2장 (1024px, 내부 2x)
  python art/render_gacha.py --quick      512px 빠른 시안
  python art/render_gacha.py --only 전설    한 등급만 (전설상 처럼 세부까지도 가능, sequence는 연출만)

출력: art/out/steps/01_재앙_하.png … 21_신화_상.png, 22~24 비정상
      art/out/sequence_승급_전설.png, art/out/sequence_강등_실패.png
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


# ------------------------------------------------------------------ 등급 사양
FAMS = {
    "재앙": dict(col=v3(0.80, 0.13, 0.06), mark="××", text=(226, 104, 88)),
    "실패": dict(col=v3(0.72, 0.60, 0.42), mark="×", text=(186, 172, 150)),
    "정상": dict(col=v3(1.00, 0.93, 0.82), mark="★", text=(255, 237, 209)),
    "준수": dict(col=v3(0.28, 0.62, 1.00), mark="★★", text=(71, 158, 255)),
    "희귀": dict(col=v3(0.66, 0.34, 1.00), mark="★★★", text=(168, 87, 255)),
    "전설": dict(col=v3(1.00, 0.70, 0.24), mark="★★★★", text=(255, 178, 61)),
    "신화": dict(col=v3(0.93, 0.92, 1.00), mark="★★★★★", text=(240, 236, 255)),
    "비정상": dict(col=v3(1.00, 1.00, 1.00), mark="??", text=(236, 234, 228)),
}
LADDER = ["재앙", "실패", "정상", "준수", "희귀", "전설", "신화"]


def subnames(fam):
    return ("미세", "뚜렷", "세계급") if fam == "비정상" else ("하", "중", "상")


def spec(fam, s):
    """등급·세부(0=하,1=중,2=상)별 연출 사양."""
    F_ = FAMS[fam]
    sp = dict(fam=fam, s=s, sub=subnames(fam)[s], col=F_["col"], mark=F_["mark"], text=F_["text"],
              step=None if fam == "비정상" else LADDER.index(fam) * 3 + s + 1,
              shell="normal", crack=1, inten=1.0, parts=20, open=False, rays=0.0, arcs=0, shards=0,
              ripple=False, smoke=0.0, ash=0, fallen=False, sink=0.0, dust=0.0, halo=False, beam=0.0,
              rainbow=False, invert=False, refl="same", tilt=0.0, streaks=0, bg="dark", seed=11 + 7 * s)
    pick = lambda xs: xs[s]  # noqa: E731
    if fam == "재앙":
        sp.update(shell="burnt", crack=pick([4, 3, 2]), inten=pick([0.75, 0.6, 0.45]), smoke=pick([1.0, 0.75, 0.5]),
                  ash=pick([160, 110, 70]), parts=0, bg="blood", shards=pick([10, 6, 3]))
    elif fam == "실패":
        sp.update(shell="dull", crack=1, inten=pick([0.22, 0.3, 0.42]), fallen=pick([True, True, False]),
                  sink=pick([34.0, 14.0, 0.0]), dust=pick([1.0, 0.8, 0.5]), parts=pick([4, 8, 14]), bg="dull",
                  smoke=pick([0.25, 0.15, 0.0]))
    elif fam == "정상":
        sp.update(crack=1, inten=pick([0.55, 0.85, 1.15]), parts=pick([10, 24, 40]))
    elif fam == "준수":
        sp.update(crack=pick([2, 2, 3]), inten=pick([1.2, 1.5, 1.85]), parts=pick([40, 60, 85]), ripple=True)
    elif fam == "희귀":
        sp.update(crack=pick([3, 3, 4]), inten=pick([1.7, 2.0, 2.4]), arcs=pick([4, 7, 11]),
                  parts=pick([70, 90, 125]), shards=pick([8, 14, 20]), ripple=True)
    elif fam == "전설":
        sp.update(open=True, crack=4, inten=pick([2.4, 3.0, 3.5]), rays=pick([0.4, 0.55, 0.75]),
                  parts=pick([120, 170, 230]), shards=pick([18, 26, 34]), ripple=True)
    elif fam == "신화":
        sp.update(open=True, crack=4, inten=pick([1.6, 1.9, 2.2]), rays=pick([0.35, 0.45, 0.55]),
                  parts=pick([200, 260, 330]), shards=pick([24, 32, 40]), ripple=True, halo=True,
                  beam=pick([0.35, 0.5, 0.7]), rainbow=True, bg="dawn")
    elif fam == "비정상":
        if s == 0:
            sp.update(crack=1, inten=0.9, parts=16, refl="black")
        else:
            sp.update(shell="dark", crack=2, inten=2.2, parts=0, invert=True, refl="white", bg="pale",
                      streaks=pick([0, 80, 140]), tilt=pick([0.0, 0.0, 13.0]), shards=14)
    return sp


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
    return aa, nxl * c - nyl * s, nxl * s + nyl * c, nzl, lx, ly


def to_frame(cx, cy, rot, lx, ly):
    c, s = math.cos(rot), math.sin(rot)
    return cx + lx * c - ly * s, cy + lx * s + ly * c


def inside_egg(lx, ly, a, b, margin=6):
    t = ly / b
    if abs(t) >= 0.97:
        return False
    return abs(lx) < a * math.sqrt(1 - t * t) * (1 + 0.13 * t) - margin


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

    for i in range({1: 1, 2: 3, 3: 5, 4: 7}[level]):
        lx0 = rng.uniform(-0.45, 0.45) * a
        ly0 = rng.uniform(-0.55, 0.15) * b
        walk(lx0, ly0, rng.uniform(0, 2 * math.pi), int(rng.uniform(9, 18) + level * 3), 3.2 if level > 1 else 2.6, 0)
        walk(lx0, ly0, rng.uniform(0, 2 * math.pi), int(rng.uniform(6, 12) + level * 2), 2.6, 0)
    return polys, widths


def zig(lx, a):
    return -0.12 * EGG["b"] + 13 * np.abs(((lx / 34.0) % 1.0) * 2 - 1) - 6.5


def background(sp, seed):
    t = Y / F
    col = sp["col"]
    d = np.hypot(X - EGG["cx"], Y - EGG["cy"])
    kind = sp["bg"]
    if kind == "pale":
        img = lerpc(v3(0.62, 0.60, 0.56), v3(0.44, 0.43, 0.42), sstep(0.0, 0.75, t))
        img = lerpc(img, v3(0.74, 0.72, 0.68), sstep(0.5, 0.85, fbm(230, seed, 5, sx=2.6)) * 0.6)
        return img * (1 - 0.55 * np.exp(-d / 240))[..., None]
    if kind == "dawn":
        top, low = v3(0.016, 0.020, 0.045), v3(0.10, 0.09, 0.13)
    elif kind == "dull":
        top, low = v3(0.016, 0.016, 0.017), v3(0.040, 0.038, 0.036)
    elif kind == "blood":
        top, low = v3(0.006, 0.005, 0.006), v3(0.030, 0.012, 0.012)
    else:
        top, low = v3(0.008, 0.010, 0.020), v3(0.020, 0.024, 0.040)
    img = lerpc(top, low, sstep(0.0, 0.75, t))
    gk = {"dawn": 0.14, "dull": 0.02, "blood": 0.05}.get(kind, 0.06)
    img += col * (np.exp(-d / 360) * gk + np.exp(-d / 170) * gk * 0.8)[..., None]
    cl = fbm(230, seed, 5, sx=2.6)
    m = sstep(0.48, 0.82, cl) * (0.35 + 0.65 * sstep(0.1, 0.65, t))
    mist = {"dull": v3(0.05, 0.048, 0.045), "blood": v3(0.035, 0.010, 0.010), "dawn": v3(0.12, 0.11, 0.15)}
    img = lerpc(img, mist.get(kind, v3(0.030, 0.033, 0.050)) + col * 0.02, m * 0.7)
    img += v3(0.02, 0.022, 0.03) * (sstep(0.55, 0.9, fbm(90, seed + 7, 4, sx=3.0)) * 0.6)[..., None]
    return img


def shell_color(nx, ny, nz, kind="normal"):
    L = np.array([-0.45, -0.70, 0.55], np.float32)
    L /= np.linalg.norm(L)
    Hh = L + np.array([0, 0, 1], np.float32)
    Hh /= np.linalg.norm(Hh)
    ndl = nx * L[0] + ny * L[1] + nz * L[2]
    wrap = np.clip((ndl + 0.35) / 1.35, 0, 1)
    sp_ = np.clip(nx * Hh[0] + ny * Hh[1] + nz * Hh[2], 0, 1)
    amb = 0.55 + 0.45 * np.clip(-ny, -1, 1)
    if kind == "dark":
        return (v3(0.012, 0.012, 0.014) * (amb * 0.6 + wrap * 0.8)[..., None]
                + v3(1, 1, 1) * (sp_ ** 90 * 1.4 + sp_ ** 14 * 0.06)[..., None])
    base = {"normal": v3(0.62, 0.58, 0.52), "dull": v3(0.40, 0.37, 0.33), "burnt": v3(0.10, 0.085, 0.08)}[kind]
    spk = {"normal": 0.30, "dull": 0.08, "burnt": 0.10}[kind]
    return base * (amb * 0.22 + wrap * 0.55)[..., None] + v3(0.9, 0.92, 1.0) * (sp_ ** 40 * spk)[..., None]


def render(sp, phase="final", crack_col=None, egg_cy=None, flash=0.0, shake=0.0, descend=False, inten_k=1.0):
    """phase: final(결과) / closed(금 없음) / crack(금+빛만, 연출용)"""
    col = sp["col"] if crack_col is None else crack_col
    seed = sp["seed"]
    rng = np.random.default_rng(seed + 1000 * (sp["step"] or 30))
    eg = dict(EGG)
    final = phase == "final"
    if sp["fallen"] and final:
        eg["rot"] = math.radians(84)
        eg["cy"] = HOR - eg["a"] * 0.92 + sp["sink"]
    if egg_cy is not None:
        eg["cy"] = egg_cy
    opened = sp["open"] and final
    level = sp["crack"] if phase in ("final", "crack") else 0
    inten = sp["inten"] * inten_k
    inv = sp["invert"] and final
    shell = sp["shell"] if final else ("normal" if sp["shell"] in ("burnt", "dull") else sp["shell"])

    img = background(sp if final else dict(sp, bg="dark"), 30 + seed)
    emi = np.zeros((N, N, 3), np.float32)

    def egg_layer(open_, level_, kind):
        lay = np.zeros((N, N, 3), np.float32)
        e = np.zeros((N, N, 3), np.float32)
        aa, nx, ny, nz, lx, ly = egg_fields(eg["cx"], eg["cy"], eg["a"], eg["b"], eg["rot"])
        speck = fbm(6, 5 + seed, 3)
        sc_ = shell_color(nx, ny, nz, kind) * (0.92 + 0.16 * speck)[..., None]
        if open_:
            zz = zig(lx, eg["a"])
            bottom = aa * np.clip((ly - zz) * SC / 0.9 + 0.5, 0, 1)
            lay += sc_ * bottom[..., None]
            al = bottom.copy()
            rim = bottom * np.exp(-np.maximum(ly - zz, 0) / 10.0)
            e += col * (rim * inten * 1.6)[..., None]
            lift = 190.0 if sp["fam"] == "신화" else 150.0
            aa2, nx2, ny2, nz2, lx2, ly2 = egg_fields(eg["cx"] + 34, eg["cy"] - lift, eg["a"], eg["b"],
                                                      eg["rot"] + math.radians(22))
            cap = aa2 * np.clip((zig(lx2, eg["a"]) - ly2) * SC / 0.9 + 0.5, 0, 1)
            cc = shell_color(nx2, ny2, nz2, kind) * (0.92 + 0.16 * speck)[..., None]
            caprim = cap * np.exp(-np.maximum(zig(lx2, eg["a"]) - ly2, 0) / 9.0)
            cc += col * (caprim * 0.9)[..., None]
            lay = lay * (1 - cap[..., None]) + cc * cap[..., None]
            al = cap + al * (1 - cap)
            e = e * (1 - cap[..., None]) + col * (caprim * inten * 0.8)[..., None]
            core = to_frame(eg["cx"], eg["cy"], eg["rot"], 0, -0.12 * eg["b"] - 30)
            ck = min(1.0, inten / 3.0)
            for r_, i_ in ((34, 3.0), (90, 0.8), (220, 0.18)):
                glow(e, core[0], core[1], r_, col * 0.7 + 0.3, i_ * ck)
        else:
            lay += sc_ * aa[..., None]
            al = aa.copy()
        if level_ > 0:
            polys, widths = make_cracks(seed + 3 * (sp["step"] or 30), level_, eg)
            cm = lines_mask(polys, widths) * aa
            thin = lines_mask(polys, [w * 0.45 for w in widths]) * aa
            lay += col * (gblur(cm, 16) * aa * 0.25 * inten)[..., None] * al[..., None]
            lay *= (1 - cm * 0.85)[..., None]
            hot = 0.15 if sp["fam"] == "재앙" else min(1.0, inten)       # 재앙 균열은 하얗게 달아오르지 않는다
            e += (col * cm[..., None] * 1.6 + thin[..., None] * 2.2 * hot) * (inten * 0.8)
            e += col * (gblur(cm, 5) * 1.2 + gblur(cm, 18) * 0.8)[..., None] * inten * 0.6
        return lay, al, e

    lay, al, e = egg_layer(opened, level, shell)
    if descend:
        trail = (np.exp(-((X - eg["cx"]) / 70) ** 2) * sstep(-50, eg["cy"] - 60, Y)
                 * (1 - sstep(eg["cy"] - 60, eg["cy"], Y)))
        emi += col * (trail * 0.25)[..., None]
        k_ = int(26 * SC)
        lay = ndi.uniform_filter1d(lay, k_, axis=0, origin=int(9 * SC))
        al = ndi.uniform_filter1d(al, k_, axis=0, origin=int(9 * SC))
    if shake > 0:
        k_ = max(1, int(shake * SC))
        lay, al, e = (ndi.uniform_filter1d(z, k_, axis=1) for z in (lay, al, e))

    edge_back = np.clip(gblur(al, 3.0) - al, 0, 1) * 3.0
    emi += col * (edge_back * (0.35 + 0.15 * level) * min(1.0, inten))[..., None]
    img = img * (1 - al[..., None]) + lay
    emi = emi * (1 - al[..., None]) + e

    # 신화: 하늘에서 내려오는 빛기둥 + 후광 고리
    if sp["beam"] > 0 and final:
        beam = np.exp(-((X - eg["cx"]) / 80) ** 2) * (1 - sstep(eg["cy"] - 80, eg["cy"], Y))
        emi += col * (beam * sp["beam"] * 0.5)[..., None]
    if sp["halo"] and final:
        core = to_frame(eg["cx"], eg["cy"], eg["rot"], 0, -0.12 * eg["b"] - 30)
        rr = np.hypot(X - core[0], (Y - core[1]) * 1.05)
        ring = np.exp(-((rr - 285) / 2.2) ** 2) * 1.2 + np.exp(-((rr - 300) / 7) ** 2) * 0.25
        emi += col * (ring * (1 - al))[..., None]

    if sp["arcs"] and final:
        arcs = []
        for i in range(sp["arcs"]):
            ang = rng.uniform(0, 2 * math.pi)
            x, y = eg["cx"] + math.cos(ang) * 144, eg["cy"] + math.sin(ang) * 192
            pts = [(x, y)]
            for _ in range(int(rng.uniform(5, 11))):
                ang += rng.normal(0, 0.5)
                x += math.cos(ang) * rng.uniform(12, 22)
                y += math.sin(ang) * rng.uniform(12, 22)
                pts.append((x, y))
            arcs.append(pts)
        am = lines_mask(arcs, [1.6] * len(arcs))
        emi += col * (am * 2.2 + gblur(am, 6) * 1.2)[..., None] + (am * 1.5)[..., None]
    if opened and sp["rays"] > 0:
        src = np.clip(emi.mean(-1) - 1.0, 0, 2.0) * (1 - al)
        core = to_frame(eg["cx"], eg["cy"], eg["rot"], 0, -0.12 * eg["b"] - 30)
        rays = radial_blur(src, core[0], core[1], 48, 0.85, 0.965)
        ang_ = np.arctan2(Y - core[1], X - core[0])
        streak = 0.55 + 0.45 * np.cos(ang_ * 9 + 0.7) ** 8 + 0.3 * np.cos(ang_ * 5 + 2.1) ** 12
        emi += col * (rays * sp["rays"] * streak)[..., None]
    if inv:
        dk = np.zeros((N, N, 3), np.float32)
        for i in range(sp["streaks"]):
            ang = rng.uniform(0, 2 * math.pi)
            r1 = rng.uniform(230, 560)
            L_ = rng.uniform(50, 140)
            glow(dk, eg["cx"] + math.cos(ang) * r1, eg["cy"] + math.sin(ang) * r1 * 0.9, rng.uniform(0.9, 1.8),
                 v3(1, 1, 1), rng.uniform(0.4, 0.9), -math.cos(ang) * L_, -math.sin(ang) * L_)
        img *= (1 - np.clip(dk[..., 0], 0, 0.85))[..., None]
        sh = int(4 * SC)
        emi = np.stack([np.roll(emi[..., 0], sh, 1), emi[..., 1], np.roll(emi[..., 2], -sh, 1)], -1)

    # 연기 (재앙·실패): 금 사이에서 피어올라 위로 퍼진다
    if sp["smoke"] > 0 and final:
        top = eg["cy"] - (0.55 * eg["b"] if not sp["fallen"] else 0.6 * eg["a"])
        up = top - Y
        xc = eg["cx"] + np.sin(up / 90.0) * 30 + up * 0.12
        wd = 36 + np.maximum(up, 0) * 0.45
        cm_ = np.exp(-((X - xc) / wd) ** 2) * sstep(top + 70, top - 10, Y)
        dens = cm_ * sstep(0.32, 0.75, fbm(38, seed + 91, 5, sx=1.0, sy=1.8)) * sp["smoke"]
        scol = lerpc(v3(0.045, 0.040, 0.040), col * 0.22, sstep(top - 160, top + 20, Y))
        if sp["fam"] == "실패":
            scol = lerpc(v3(0.05, 0.048, 0.045), v3(0.08, 0.075, 0.07), sstep(top - 160, top, Y))
        img = lerpc(img, scol, dens * 0.85)
        emi *= (1 - dens * 0.6)[..., None]
    if sp["dust"] > 0 and final:
        for i in range(9):
            glow(img, eg["cx"] + rng.normal(0, 120), HOR - rng.uniform(0, 30), rng.uniform(24, 56),
                 v3(0.05, 0.047, 0.043), 0.5 * sp["dust"])

    # 파편
    if sp["shards"] and final:
        for i in range(sp["shards"]):
            if opened:
                ang, rr = rng.uniform(-math.pi, 0.15), rng.uniform(190, 400)
                x, y = eg["cx"] + math.cos(ang) * rr, eg["cy"] - 40 + math.sin(ang) * rr * 0.9
            elif sp["fam"] == "재앙":
                x, y = eg["cx"] + rng.normal(0, 150), HOR - rng.uniform(4, 40)
            else:
                ang, rr = rng.uniform(0, 2 * math.pi), rng.uniform(210, 290)
                x, y = eg["cx"] + math.cos(ang) * rr, eg["cy"] - 40 + math.sin(ang) * rr * 0.75
            s_ = rng.uniform(8, 22)
            rot = rng.uniform(0, 2 * math.pi)
            pts = [(x + math.cos(rot + k * 2.1 + rng.normal(0, 0.3)) * s_, y + math.sin(rot + k * 2.1 + rng.normal(0, 0.3)) * s_)
                   for k in range(3)]
            pm = poly_mask(pts)
            fc = {"dark": v3(0.01, 0.01, 0.012), "burnt": v3(0.02, 0.017, 0.016)}.get(
                sp["shell"], v3(0.50, 0.47, 0.42) * rng.uniform(0.12, 0.36))
            img = img * (1 - pm[..., None]) + fc * pm[..., None]
            ed = np.clip(gblur(pm, 1.2) - pm * 0.6, 0, 1)
            emi = emi * (1 - pm[..., None]) + col * (ed * (0.9 if sp["fam"] != "재앙" else 0.3))[..., None]

    # 입자: 빛 가루(위로) / 재(아래로)
    n_parts = sp["parts"] if final else sp["parts"] // 3
    for i in range(n_parts):
        ang, rr = rng.uniform(0, 2 * math.pi), rng.uniform(170, 470)
        x, y = eg["cx"] + math.cos(ang) * rr, eg["cy"] + math.sin(ang) * rr * 0.85 - rng.uniform(0, 80)
        if y > HOR - 5:
            continue
        pc = col if sp["fam"] != "실패" else v3(0.5, 0.46, 0.4)
        glow(emi, x, y, rng.uniform(0.8, 2.2), pc, rng.uniform(0.3, 1.6) * (1.6 if opened else 1.0) * min(1, inten),
             0, -rng.uniform(4, 16))
    if sp["ash"] and final:
        ab = np.zeros((N, N, 3), np.float32)
        for i in range(sp["ash"]):
            glow(ab, rng.uniform(40, 984), rng.uniform(0, HOR - 10), rng.uniform(0.9, 2.0), v3(1, 1, 1),
                 rng.uniform(0.4, 1.0), rng.normal(0, 2), rng.uniform(4, 10))
        img = lerpc(img, v3(0.09, 0.085, 0.08), np.clip(ab[..., 0], 0, 1) * 0.7)
        for i in range(sp["ash"] // 6):
            glow(emi, rng.uniform(150, 870), rng.uniform(200, HOR - 10), rng.uniform(0.8, 1.4), col,
                 rng.uniform(0.2, 0.7), 0, rng.uniform(3, 8))

    # 수면 반사 (비정상은 다른 알이 비친다)
    refl_src = img + emi
    if sp["refl"] != "same" and final:
        lay2, al2, _ = egg_layer(False, 0, "normal" if sp["refl"] == "white" else "dark")
        bgk = 0.45 if sp["refl"] == "white" else 1.0
        refl_src = (background(sp, 30 + seed) * bgk * (1 - al2[..., None])
                    + lay2 * (3.2 if sp["refl"] == "white" else 1.0))
    rip = (fbm(40, 77 + seed, 3, sx=3.0, sy=0.4) - 0.5) * 10
    sy_ = np.clip((2 * HOR - Y) * SC, 0, N - 1)
    sx_ = np.clip((X + rip) * SC, 0, N - 1)
    refl = gblur(np.stack([ndi.map_coordinates(refl_src[..., c], [sy_, sx_], order=1) for c in range(3)], -1), 2.5)
    water = sstep(HOR - 1, HOR + 1, Y)
    depth = sstep(HOR, F, Y)
    wcol = v3(0.012, 0.012, 0.014) if inv else v3(0.006, 0.008, 0.014)
    refl_k = (0.75 - 0.2 * depth) if inv else (0.55 - 0.25 * depth)
    img = lerpc(img, wcol + refl * refl_k[..., None], water)
    emi *= (1 - water)[..., None]
    if sp["ripple"] and final:
        rr_ = np.hypot((X - eg["cx"]) / 3.2, (Y - (HOR + 40)))
        for R_ in (30, 52, 78):
            emi += col * (np.exp(-((rr_ - R_) / 1.6) ** 2) * water * 0.5 * (90 - R_) / 60)[..., None]
    if flash > 0:
        glow(emi, eg["cx"], eg["cy"], 220, v3(1, 0.95, 0.85), flash)
    if sp["rainbow"] and final:
        ang_ = np.arctan2(Y - eg["cy"], X - eg["cx"])
        rb = np.stack([0.5 + 0.5 * np.cos(ang_ * 2 + o) for o in (0.0, 2.09, 4.19)], -1)
        emi *= 0.45 + 1.1 * rb
    return img, emi, al


def finish(img, emi, egg_a, sp, label=True, out_path=None, paint=True, caption=None, tilt=0.0):
    img = img + emi
    br = np.maximum(img - 0.9, 0) * 0.6 + np.maximum(emi, 0) * 0.5
    img = img + gblur(br, 3) * 0.45 + gblur(br, 14) * 0.35 + gblur(br, 50) * 0.3
    if SS > 1:
        img, egg_a, emif = _down(img, SS), _down(egg_a, SS), _down(emi, SS)
    else:
        emif = emi
    x = np.maximum(img, 0)
    tm = np.clip((x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14), 0, 1)
    srgb = np.where(tm <= 0.0031308, tm * 12.92, 1.055 * np.power(tm, 1 / 2.4) - 0.055).astype(np.float32)
    srgb = np.clip(srgb + 0.5 * (srgb - 0.42) * srgb * (1 - srgb), 0, 1)
    h = srgb.shape[0]
    s_ = h / 1024
    if paint:
        lay = [(max(2, int(16 * s_)), 0.05, 7, 235), (max(2, int(8 * s_)), 0.045, 9, 225),
               (max(1, int(4 * s_ + 0.5)), 0.04, 10, 215)]
        pt = stroke_paint(srgb, lay, seed=(sp["step"] or 30))
        focal = np.clip(emif.max(-1) * 0.6, 0, 1)
        k = (0.85 * (1 - egg_a) + 0.6 * egg_a) * (1 - 0.55 * ndi.gaussian_filter(focal, 2 * s_))
        srgb = lerpc(srgb, pt, k)
    fy, fx = np.mgrid[0:h, 0:h].astype(np.float32) / h
    srgb *= (1 - 0.35 * np.clip(((fx - 0.5) * 1.5) ** 2 + ((fy - 0.47) * 1.4) ** 2, 0, 1.5) ** 1.3)[..., None]
    if label:
        srgb *= (1 - 0.5 * sstep(0.84, 0.97, fy))[..., None]
    srgb += (np.random.default_rng(5).normal(0, 1, (h, h)).astype(np.float32) * 0.008)[..., None]
    im = Image.fromarray((np.clip(srgb, 0, 1) * 255 + 0.5).astype(np.uint8))
    if tilt:
        z = math.cos(math.radians(tilt)) + math.sin(math.radians(abs(tilt)))
        big = im.resize((int(h * z), int(h * z)), Image.BICUBIC).rotate(tilt, Image.BICUBIC)
        o = (big.size[0] - h) // 2
        im = big.crop((o, o, o + h, o + h))
    d = ImageDraw.Draw(im)
    if label:
        f1, f2 = ImageFont.truetype(FONT_B, int(46 * s_)), ImageFont.truetype(FONT_B, int(30 * s_))
        name = f"【{sp['fam']} · {sp['sub']}】"
        line2 = sp["mark"] if sp["step"] is None else f"{sp['mark']}  ·  {sp['step']}단계"
        y0 = int(912 * s_)
        d.text(((h - d.textlength(name, font=f1)) / 2, y0), name, font=f1, fill=sp["text"])
        d.text(((h - d.textlength(line2, font=f2)) / 2, y0 + int(58 * s_)), line2, font=f2, fill=sp["text"])
    if caption:
        d.text((int(36 * s_), int(30 * s_)), caption, font=ImageFont.truetype(FONT_B, int(40 * s_)), fill=(235, 232, 225))
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        im.save(out_path)
        log(f"saved {out_path.relative_to(OUT)}")
    return im


def all_specs():
    for fam in LADDER + ["비정상"]:
        for s in range(3):
            yield spec(fam, s)


def step_file(sp):
    no = sp["step"] if sp["step"] else 21 + sp["s"] + 1
    return OUT / "steps" / f"{no:02d}_{sp['fam']}_{sp['sub']}.png"


def sheet(tiles, path):
    s = tiles[0].size[0]
    out = Image.new("RGB", (s * 2 + 12, s * 2 + 12), (8, 9, 12))
    for i, t in enumerate(tiles):
        out.paste(t, ((i % 2) * (s + 12), (i // 2) * (s + 12)))
    out.save(path)
    log(f"saved {path.name}")


def main():
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    for sp in all_specs():
        if only and only not in (sp["fam"], f"{sp['fam']}{sp['sub']}"):
            continue
        img, emi, al = render(sp)
        finish(img, emi, al, sp, out_path=step_file(sp), tilt=sp["tilt"])
    if only and only != "sequence":
        return
    blue, gold, dull = FAMS["준수"]["col"], FAMS["전설"]["col"], FAMS["실패"]["col"]
    leg = spec("전설", 1)
    frames = [("① 강림", render(leg, phase="closed", crack_col=blue, egg_cy=300, descend=True)),
              ("② 균열 · 파란빛", render(leg, phase="crack", crack_col=blue)),
              ("③ 승급 · 빛이 바뀐다", render(leg, phase="crack", crack_col=blue * 0.35 + gold * 0.65, flash=0.15, shake=14)),
              ("④ 개화 · 【전설】", render(leg, phase="final"))]
    sheet([finish(i, e, a, leg, label=False, caption=c) for c, (i, e, a) in frames], OUT / "sequence_승급_전설.png")
    fail = spec("실패", 1)
    frames = [("① 강림", render(fail, phase="closed", crack_col=gold, egg_cy=300, descend=True)),
              ("② 균열 · 금빛…?", render(dict(fail, crack=2), phase="crack", crack_col=gold, inten_k=5.0)),
              ("③ 강등 · 빛이 꺼진다", render(dict(fail, crack=2), phase="crack", crack_col=dull, inten_k=0.6, shake=10)),
              ("④ 굴러떨어짐 · 【실패】", render(fail, phase="final"))]
    sheet([finish(i, e, a, fail, label=False, caption=c) for c, (i, e, a) in frames], OUT / "sequence_강등_실패.png")


if __name__ == "__main__":
    main()
