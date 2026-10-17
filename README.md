# 정상

크랙 캐릭터챗. 0살부터 시작하는 초·중·고 + 인생 시뮬레이션. 부모와 재능은 **삼신 가챠**로 정해지고, 가끔 세상이 한 군데만 비틀린다(초현실).

## 구성

| 경로 | 내용 |
|---|---|
| `prompt/gacha_block.txt` | 크랙 프롬프트에 붙이는 가챠 블록 (`<gacha_system>`) |
| `docs/GACHA.md` | 가챠 설계 근거: 확률, 천장, 연출, 시뮬레이션 결과 |
| `art/out/` | 등급 이미지 5장, 연출 4컷, 작동 방식 안내 이미지 |
| `art/render_gacha.py` | 등급 이미지·연출 렌더러 (`--quick`으로 시안) |
| `art/render_guide.py` | 작동 방식 안내 이미지 렌더러 |
| `tools/gacha_sim.py` | 가챠 규칙 기준 구현 + 구간표 생성 + 확률 시뮬레이션 |

## 다시 만들기

```bash
python tools/gacha_sim.py
python art/render_gacha.py
python art/render_guide.py
```

필요한 것: Python 3, numpy, scipy, Pillow, 맑은 고딕(Windows 기본 폰트).
