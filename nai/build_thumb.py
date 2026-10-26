"""정상 — 크랙 썸네일용 NAI 프롬프트 3종 → nai/thumbnail_prompts.txt

  python nai/build_thumb.py

화풍·네거는 build_nai.py와 같은 것을 가져다 쓴다(88종 이미지와 톤을 맞추려고).
"""
from pathlib import Path

from build_nai import CHAR_NEG, CHILD_NEG, EXPR, NEG, SETTINGS, STYLE

HERE = Path(__file__).parent

# (제목, 한 줄 설명, 인원 태그, 장면, 캐릭터, 아이 여부)
THUMBS = [
    ("① 알이 내려오는 밤 (추천)",
     "아파트 옥상에서 아이가 하늘을 올려다본다. 등불처럼 내려오는 알 수십 개 중 하나만 금빛으로 깨진다. 뒷모습이라 성별·얼굴을 정하지 않아도 된다.",
     "1boy, solo",
     "korean apartment complex at night, rooftop, 1.3::countless glowing eggs floating down from the night sky like lanterns::, "
     "1.2::one golden egg cracking open with light rays::, surreal, vast night sky, city lights below, deep blue, wide shot, from behind",
     "child, boy, short black hair, navy hoodie, school backpack, standing, looking up, from behind",
     True),
    ("② 삼신할미",
     "얼굴이 보이는 캐릭터형 썸네일. 금이 간 알 하나를 두 손으로 내미는 삼신할미, 뒤로 알 선반.",
     "1girl, solo, old woman",
     "traditional korean room, wooden shelves full of glowing eggs, candlelight, hearth, steam, warm lighting, upper body",
     "1.2::old woman, elderly, wrinkled face::, grandmother, white hair, hair bun, 1.2::white hanbok, korean traditional clothes::, "
     "round glasses on nose, holding a glowing egg in both hands, offering egg to viewer, 1.2::golden light leaking from cracks in the egg::, "
     + EXPR["기본"],
     False),
    ("③ 평범한 등굣길",
     "제목 '정상'의 반어. 아주 평범한 아침 등굣길인데 해 자리에 금 간 거대한 알이 떠 있고, 아무도 신경 쓰지 않는다.",
     "1girl, solo",
     "korean residential street, morning, crosswalk, apartment buildings, school route, "
     "1.3::giant cracked egg in the sky instead of the sun, golden light from the crack::, surreal, everyday life, wide shot, from below",
     "child, girl, elementary school student, black hair, low twintails, black eyes, yellow hat, red school backpack, "
     "white t-shirt, overalls, walking, looking up, surprised, open mouth",
     True),
]


def main():
    lines = [
        "정상 · 크랙 썸네일용 NAI 프롬프트 3종",
        f"설정: {SETTINGS['model']} · {SETTINGS['steps']} steps · scale {SETTINGS['scale']} · {SETTINGS['sampler']} · {SETTINGS['noise_schedule']}",
        "크기: 정사각 1024x1024 (세로 썸네일이면 832x1216). 칸마다 그대로 복사.",
        "글자는 NAI가 못 쓰니 제목 '정상'은 뽑은 뒤 따로 얹는다.",
        "",
    ]
    for title, desc, count, scene, char, child in THUMBS:
        cneg = CHAR_NEG + (", " + CHILD_NEG if child else "")
        lines += ["=" * 60, title, desc, "=" * 60,
                  "■ 베이스 프롬프트", f"{count}, {scene}, {STYLE}", "",
                  "■ 캐릭터 프롬프트", char, "",
                  "■ 캐릭터 네거", cneg, "",
                  "■ Undesired Content", NEG, "", ""]
    out = HERE / "thumbnail_prompts.txt"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
