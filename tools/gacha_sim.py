"""삼신 가챠 규칙의 기준 구현 + 확률 검증.

  python tools/gacha_sim.py          구간표(프롬프트용)와 실효 확률 출력
  python tools/gacha_sim.py --md     docs에 붙일 마크다운 표 출력

프롬프트(prompt/gacha_block.txt)의 구간표는 이 파일의 range_table()에서 나온 것이다.
규칙을 바꾸면 여기부터 고치고 표를 다시 뽑는다.
"""
import random
import sys
from collections import Counter

TIERS = ["비정상", "전설", "희귀", "준수", "정상"]          # d1000 구간 배치 순서 (작은 수부터)
BASE = {"비정상": 10, "전설": 35, "희귀": 105, "준수": 250, "정상": 600}   # 1000분율
GAUGE_MAX = 10          # 눈치 게이지가 10이면 다음 1회는 희귀 이상 확정
LEGEND_PITY = 30        # 전설 없이 30회 뽑으면 다음은 전설 확정


def weights(gauge, legend_miss, birth_guard):
    """현재 상태에서의 1000분율 가중치."""
    if legend_miss >= LEGEND_PITY:
        return {"비정상": 0, "전설": 1000, "희귀": 0, "준수": 0, "정상": 0}
    if gauge >= GAUGE_MAX:
        return {"비정상": 0, "전설": 250, "희귀": 750, "준수": 0, "정상": 0}
    w = dict(BASE)
    w["희귀"] += 15 * gauge          # 게이지 1당 희귀 +1.5%p, 전설 +0.5%p, 정상 -2%p
    w["전설"] += 5 * gauge
    w["정상"] -= 20 * gauge
    if birth_guard:                  # 출생 5연차의 5번째인데 앞 4장이 전부 '정상'
        w["정상"] = 0
    return w


def range_table(birth_guard=False, gauges=range(GAUGE_MAX)):
    rows = []
    for g in gauges:
        w = weights(g, 0, birth_guard)
        tot = sum(w.values())
        last = max(i for i, t in enumerate(TIERS) if w[t] > 0)
        lo, cells = 1, []
        for i, t in enumerate(TIERS):
            n = round(w[t] * 1000 / tot)
            if n <= 0:
                cells.append((t, None, None))
                continue
            hi = 1000 if i == last else lo + n - 1
            cells.append((t, lo, hi))
            lo = hi + 1
        rows.append((g, cells))
    return rows


def pull(state, rng, birth_guard=False):
    w = weights(state["gauge"], state["legend_miss"], birth_guard)
    r = rng.random() * sum(w.values())
    for t in TIERS:
        if r < w[t]:
            break
        r -= w[t]
    if t in ("희귀", "전설"):
        state["gauge"] = 0
    elif t in ("정상", "준수"):
        state["gauge"] += 1
    state["legend_miss"] = 0 if t == "전설" else state["legend_miss"] + 1
    return t


def life(rng, extra=0):
    """출생 5연차(부·모·재능3) + 성장 가챠 4회(입학 3번·성인) + 복으로 산 추가분."""
    st = {"gauge": 0, "legend_miss": 0}
    out = []
    for i in range(5):
        guard = i == 4 and all(t == "정상" for t in out)
        out.append(pull(st, rng, guard))
    birth = list(out)
    for _ in range(4 + extra):
        out.append(pull(st, rng))
    return birth, out


def main():
    rng = random.Random(42)
    N = 200_000
    single = Counter()
    birth_best = Counter()
    any_legend = 0
    any_abn = 0
    total = Counter()
    order = {t: i for i, t in enumerate(["정상", "준수", "희귀", "전설", "비정상"])}
    for _ in range(N):
        birth, allp = life(rng)
        single[birth[0]] += 1
        birth_best[max(birth, key=lambda t: order[t] if t != "비정상" else 3.5)] += 1
        any_legend += "전설" in allp
        any_abn += "비정상" in allp
        total.update(allp)
    n_all = sum(total.values())

    md = "--md" in sys.argv
    print("## d1000 구간표 (눈치 게이지별)\n" if md else "[d1000 구간표]")
    if md:
        print("| 게이지 | 비정상 | 전설 | 희귀 | 준수 | 정상 |")
        print("|---|---|---|---|---|---|")
    for g, cells in range_table():
        if md:
            print(f"| {g} | " + " | ".join(f"{a}–{b}" if a else "—" for _, a, b in cells) + " |")
        else:
            print(f"G{g}: " + " / ".join(f"{t} {a}-{b}" if a else f"{t} -" for t, a, b in cells))
    print()
    print("[출생 5연차 마지막 장, 앞 4장이 전부 정상일 때 — 게이지는 이때 항상 4]")
    for g, cells in range_table(birth_guard=True, gauges=[4]):
        print(f"G{g}: " + " / ".join(f"{t} {a}-{b}" if a else f"{t} -" for t, a, b in cells))
    print()
    print(f"[시뮬레이션 {N:,}명 인생, 1인당 9뽑]")
    print("첫 장(게이지 0) 실측:", {t: f"{single[t] / N * 100:.1f}%" for t in TIERS})
    print("전체 뽑기 실효 확률:", {t: f"{total[t] / n_all * 100:.2f}%" for t in TIERS})
    print("출생 5연차 최고 등급:", {t: f"{birth_best[t] / N * 100:.1f}%" for t in TIERS})
    print(f"평생 9뽑 중 전설 1장 이상: {any_legend / N * 100:.1f}%")
    print(f"평생 9뽑 중 비정상 1장 이상: {any_abn / N * 100:.1f}%")


if __name__ == "__main__":
    main()
