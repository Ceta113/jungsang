# 정상

크랙 캐릭터챗. 0살부터 시작하는 초·중·고 + 인생 시뮬레이션. 부모와 재능은 **삼신 가챠**로 정해지고, 가끔 세상이 한 군데만 비틀린다(초현실).

삼신 가챠는 재앙부터 신화까지 7등급 × 하·중·상 = 21단계에 비정상 3단계가 더해진다. 실패에는 보상과 극복 루트가 있다.

**가챠 실행기 웹사이트: https://ceta113.github.io/jungsang/** (GitHub Pages, `gh-pages` 브랜치 = `web/` 폴더)

## 구성

| 경로 | 내용 |
|---|---|
| `prompt/jungsang_prompt.txt` | **크랙에 넣는 완성 프롬프트** (7000자 이내, 인생 시뮬 + 압축 가챠). `python tools/build_prompt.py`로 다시 만든다 |
| `prompt/start_settings.txt` | 시작설정 3종 (① 분만실 ② 삼신할미의 방 ③ 초등학교 입학식) |
| `nai/nai_prompts_full.txt` | NovelAI V5 이미지 프롬프트 88종 완성본 (주인공 나이별·가족·친구·선생님·장면). `python nai/build_nai.py`로 다시 만든다 |
| `nai/nai_prompts.md` | 같은 내용의 읽기용 목록 + 표정표 (JSON은 `nai/nai_prompts.json`) |
| `nai/images/` | 위 프롬프트로 뽑은 이미지 88장. 이름이 전부 `기본_<행>.png`라 크랙 이미지 표가 열 1개 × 행 88개로 빈칸 없이 찬다 (목록은 `INDEX.md`). 용량이 커서 PNG는 git에 안 올리고 로컬에만 둔다. 전체 미리보기는 `nai/preview.jpg` |
| `nai/gen_images.py` | NAI 일괄 생성·검수 시트·이름 정리 (`gen` / `sheet` / `final`) |
| `prompt/gacha_block.txt` | 가챠 규칙 풀버전 (설명용, 길이 제한 없음) |
| `docs/GACHA.md` | 가챠 설계 근거: 확률, 천장, 실패 보상, 연출, 시뮬레이션 결과 |
| `art/out/steps/` | 단계 이미지 24장 (01_재앙_하 ~ 21_신화_상, 22~24 비정상) |
| `art/out/` | 연출 4컷 2종(승급·강등), 작동 방식 안내 이미지 |
| `art/render_gacha.py` | 단계 이미지·연출 렌더러 (`--quick`으로 시안, `--only 전설`로 한 등급만) |
| `art/render_guide.py` | 작동 방식 안내 이미지 렌더러 |
| `web/index.html` | 가챠 실행기 (연출·카드 텍스트·확률 검증). `python -m http.server --directory web` 후 브라우저로 연다 |
| `tools/gacha_sim.py` | 가챠 규칙 기준 구현 + 구간표 생성 + 확률 시뮬레이션 |

## 다시 만들기

```bash
python tools/gacha_sim.py
python art/render_gacha.py
python art/render_guide.py
```

필요한 것: Python 3, numpy, scipy, Pillow, 맑은 고딕(Windows 기본 폰트).

## 웹사이트 업데이트

`web/`을 고쳐 main에 커밋한 뒤, `web/` 폴더만 `gh-pages` 브랜치로 올리면 1~2분 뒤 사이트에 반영된다.

```bash
git push origin main
git subtree push --prefix web origin gh-pages
```
