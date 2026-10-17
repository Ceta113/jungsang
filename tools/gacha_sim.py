"""삼신 가챠 규칙의 기준 구현 + 확률 검증 (7등급 × 하·중·상 = 21단계 + 비정상 3단계).

  python tools/gacha_sim.py          프롬프트용 구간표와 실효 확률 출력
  python tools/gacha_sim.py --md     docs에 붙일 마크다운 표 출력

굴림은 두 번이다.
  1차 d10000 → 등급 (눈치 게이지별 구간표)
  2차 d100   → 하·중·상 (등급마다 고정 분할)
프롬프트(prompt/gacha_block.txt)의 표는 전부 이 파일에서 나온 값이다. 규칙을 바꾸면 여기부터 고친다.
"""
import random
import sys
from collections import Counter

# 1차 굴림 구간 배치 순서 (작은 수부터)
ORDER = ["비정상", "신화", "전설", "희귀", "준수", "정상", "실패", "재앙"]
LADDER = ["재앙", "실패", "정상", "준수", "희귀", "전설", "신화"]          # 나쁨 → 좋음
BASE = {"비정상": 100, "신화": 50, "전설": 350, "희귀": 1100, "준수": 2400,
        "정상": 4500, "실패": 1200, "재앙": 300}                         # 만분율, 합 10000
PER_G = {"희귀": +120, "전설": +35, "신화": +5, "정상": -50, "실패": -80, "재앙": -30}
GAUGE_MAX = 10
SURE = {"희귀": 7600, "전설": 2100, "신화": 300}                         # 눈치 10 확정
TOP_PITY = 40                                                             # 전설 이상 없이 40장 → 전설 확정
GAIN = {"재앙": 2, "실패": 2, "정상": 1, "준수": 1}                       # 게이지 증가량
BOK_REFUND = {"재앙": 25, "실패": 10}                                     # 삼신의 사과

# 2차 굴림 d100: (하 끝, 중 끝) — 나머지는 상
SUB = {"재앙": (15, 50), "실패": (15, 50), "정상": (30, 70), "준수": (50, 85),
       "희귀": (50, 85), "전설": (55, 88), "신화": (60, 92), "비정상": (60, 90)}
SUBNAME = {"비정상": ("미세", "뚜렷", "세계급")}
GOOD = {"준수", "희귀", "전설", "신화"}


def step_no(fam, sub):
    """1(재앙·하) ~ 21(신화·상). 비정상은 None."""
    if fam == "비정상":
        return None
    return LADDER.index(fam) * 3 + sub + 1


def weights(g, top_miss, birth_guard=False):
    if top_miss >= TOP_PITY:
        return {"전설": 10000}
    if g >= GAUGE_MAX:
        return dict(SURE)
    w = {k: v + PER_G.get(k, 0) * g for k, v in BASE.items()}
    if birth_guard:                    # 출생 5연차 마지막 장인데 준수 이상이 하나도 없었다
        for k in ("재앙", "실패", "정상"):
            w[k] = 0
    return w


def range_table(gauges=range(GAUGE_MAX), birth_guard=False):
    rows = []
    for g in gauges:
        w = weights(g, 0, birth_guard)
        tot = sum(w.values())
        live = [k for k in ORDER if w.get(k, 0) > 0]
        lo, cells = 1, []
        for k in ORDER:
            n = round(w.get(k, 0) * 10000 / tot)
            if n <= 0:
                cells.append((k, None, None))
                continue
            hi = 10000 if k == live[-1] else lo + n - 1
            cells.append((k, lo, hi))
            lo = hi + 1
        rows.append((g, cells))
    return rows


def roll_sub(fam, rng):
    a, b = SUB[fam]
    r = rng.randint(1, 100)
    return 0 if r <= a else (1 if r <= b else 2)


def pull(st, rng, birth=None):
    guard = birth is not None and birth["i"] == 4 and not birth["good"]
    w = weights(st["g"], st["top_miss"], guard)
    r = rng.random() * sum(w.values())
    for fam in ORDER:
        if r < w.get(fam, 0):
            break
        r -= w.get(fam, 0)
    sub = roll_sub(fam, rng)
    if birth is not None and fam == "재앙":
        if birth["calamity"]:
            fam, sub = "실패", 0          # 출생에서 두 번째 재앙은 실패·하로 감면
        else:
            birth["calamity"] = True
    if fam in ("희귀", "전설", "신화"):
        st["g"] = 0
    elif fam != "비정상":
        st["g"] = min(GAUGE_MAX, st["g"] + GAIN[fam])
    st["top_miss"] = 0 if fam in ("전설", "신화") else st["top_miss"] + 1
    st["bok"] += BOK_REFUND.get(fam, 0)
    if birth is not None:
        birth["good"] |= fam in GOOD
        birth["i"] += 1
    return fam, sub


def life(rng):
    st = {"g": 0, "top_miss": 0, "bok": 0}
    b = {"i": 0, "good": False, "calamity": False}
    birth = [pull(st, rng, b) for _ in range(5)]
    grow = [pull(st, rng) for _ in range(4)]
    return birth, grow, st


def main():
    md = "--md" in sys.argv
    rng = random.Random(42)
    N = 200_000
    first = Counter()
    steps = Counter()
    fams = Counter()
    any_ = Counter()
    birth_best = Counter()
    bok = 0
    for _ in range(N):
        st0 = {"g": 0, "top_miss": 0, "bok": 0}
        first[pull(st0, rng)] += 1
        birth, grow, st = life(rng)
        allp = birth + grow
        for f, s in allp:
            fams[f] += 1
            steps[(f, s)] += 1
        for f in set(f for f, _ in allp):
            any_[f] += 1
        best = max((f for f, _ in birth if f != "비정상"), key=LADDER.index, default="정상")
        birth_best[best] += 1
        bok += st["bok"]
    tot = sum(fams.values())

    print("[1차 굴림 d10000 — 눈치 게이지별 구간표]")
    for g, cells in range_table():
        print(f"G{g}: " + " / ".join(f"{k} {a}-{b}" if a else f"{k} -" for k, a, b in cells))
    print("G10(확정): " + " / ".join(f"{k} {v / 100:.0f}%" for k, v in SURE.items()))
    print("\n[출생 보장표 — 5번째 장, 앞 4장에 준수 이상이 없을 때 (게이지는 4~8)]")
    for g, cells in range_table(gauges=range(4, 9), birth_guard=True):
        print(f"G{g}: " + " / ".join(f"{k} {a}-{b}" if a else f"{k} -" for k, a, b in cells))
    print("\n[2차 굴림 d100 — 하·중·상]")
    for f, (a, b) in SUB.items():
        n = SUBNAME.get(f, ("하", "중", "상"))
        print(f"{f}: {n[0]} 1-{a} / {n[1]} {a + 1}-{b} / {n[2]} {b + 1}-100")

    print(f"\n[시뮬레이션 {N:,}명, 1인당 9뽑 (출생 5 + 성장 4)]")
    print("첫 장(게이지 0) 실측: " +
          ", ".join(f"{f} {sum(v for (ff, _), v in first.items() if ff == f) / N * 100:.2f}%" for f in ORDER))
    print("전체 실효 확률(등급): " + ", ".join(f"{f} {fams[f] / tot * 100:.2f}%" for f in ORDER))
    print("단계별 실효 확률:")
    for f in LADDER + ["비정상"]:
        n = SUBNAME.get(f, ("하", "중", "상"))
        print(f"  {f}: " + " / ".join(f"{n[s]} {steps[(f, s)] / tot * 100:.3f}%" for s in range(3)))
    print("평생 9뽑 중 1장 이상 받는 사람: " + ", ".join(f"{f} {any_[f] / N * 100:.1f}%" for f in ORDER))
    print("출생 5연차 최고 등급(비정상 제외): " + ", ".join(f"{f} {birth_best[f] / N * 100:.1f}%" for f in LADDER))
    print(f"실패·재앙 보상으로 받는 복 평균: {bok / N:.1f}")


if __name__ == "__main__":
    main()
