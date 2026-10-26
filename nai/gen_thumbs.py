"""썸네일 후보 생성: build_thumb.py의 3종을 각 N장 → nai/raw/thumbs/

  python nai/gen_thumbs.py [N]        (기본 2장씩)
  python nai/gen_thumbs.py pick 파일   채택본을 nai/thumbnail.png로 복사
"""
import random, shutil, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_nai import CHAR_NEG, CHILD_NEG, NEG, STYLE
from build_thumb import THUMBS
from gen_images import RAW, anlas, decode, payload, request_image

OUT = RAW / "thumbs"
SIZE = [1024, 1024]


def main(n):
    OUT.mkdir(parents=True, exist_ok=True)
    tier, a0 = anlas()
    print(f"tier={tier} 시작 anlas={a0}", flush=True)
    for i, (title, _, count, scene, char, child) in enumerate(THUMBS, 1):
        a = dict(size=SIZE, base=f"{count}, {scene}, {STYLE}", negative=NEG, character=char,
                 character_negative=CHAR_NEG + (", " + CHILD_NEG if child else ""))
        for j in range(1, n + 1):
            seed = random.randint(1, 2**32 - 1)
            r = request_image(payload(a, seed))
            if r.status_code != 200:
                print(f"{title} #{j} 실패 {r.status_code}: {r.text[:200]}", flush=True)
                continue
            f = OUT / f"t{i}_{j}_{seed}.png"
            f.write_bytes(decode(r.content))
            print(f"{title} #{j} → {f.name}", flush=True)
            time.sleep(1.0)
    _, a1 = anlas()
    print(f"끝 anlas={a1} (소모 {a0 - a1})")


if __name__ == "__main__":
    if sys.argv[1:2] == ["pick"]:
        shutil.copy2(OUT / sys.argv[2], Path(__file__).parent / "thumbnail.png")
        print("→ nai/thumbnail.png")
    else:
        main(int(sys.argv[1]) if len(sys.argv) > 1 else 2)
