"""정상 — NAI 이미지 일괄 생성·검수·정리.

  python nai/gen_images.py check          토큰·Anlas 확인
  python nai/gen_images.py gen [키 ...]    아직 없는 항목(또는 지정한 키)을 한 장씩 생성 → nai/raw/
  python nai/gen_images.py sheet          검수 시트 → nai/raw/sheets/
  python nai/gen_images.py final          채택본을 알아보기 쉬운 이름으로 nai/images/에 모음 + 목록

토큰은 사용자 환경변수 NOVELAI_TOKEN에서만 읽는다(캐릭터_이미지생성/gen.py와 같은 방식). 출력·저장하지 않는다.
REUSE에 있는 항목은 생성하지 않고 기존 이미지를 가져다 쓴다.
"""
import io, json, os, random, shutil, sys, time, zipfile
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
from build_nai import ENTRIES, SETTINGS, assemble

HERE = Path(__file__).parent
RAW = HERE / "raw"
FINAL = HERE / "images"
STATE = RAW / "state.json"

CHARACTER_DIR = Path.home() / "OneDrive" / "바탕 화면" / "캐릭터_이미지생성" / "결과"
DOWNLOADS = Path(r"D:\사용자데이터\Downloads")
# 기존 이미지 재사용: 키 → (원본 경로, 메모)
_DL_BOY = "0.5__artist_sangobob__, 0.8__artist_ratatatat74 __, 1.0__artist_patzzi__, 1.0__a s-{}.png"
REUSE = {
    "f_mid_f": (CHARACTER_DIR / "교실" / "응시_교실.png", "차서은 (캐릭터_이미지생성/결과)"),
    "f_high_f": (CHARACTER_DIR / "수학" / "옅은미소_수학.png", "차서은 (캐릭터_이미지생성/결과)"),
    "f_high_m": (DOWNLOADS / _DL_BOY.format(1163119246), "다운로드 폴더 남캐"),
    "rival_m": (DOWNLOADS / _DL_BOY.format(3904887218), "다운로드 폴더 남캐"),
    "rival_f": (DOWNLOADS / "루시" / "루시_감독2.png", "루시 (다운로드/루시)"),
}
for _k, (_p, _) in REUSE.items():
    assert _p.exists(), _p

# 크랙 이미지 표는 파일 이름을 첫 '_'에서 잘라 앞은 열(감정), 뒤는 행(상황)으로 쓴다. 빈칸이 있으면 안 되므로
# 인물당 한 장인 여기서는 열을 PREFIX 하나로 통일한다 → '기본_엄마_다정.png' = 열 '기본' × 행 '엄마_다정'.
PREFIX = "기본"
# 최종 파일 이름의 행 부분(확장자 없이).
FILES = {
    "p_baby": "주인공_0세_아기", "p_toddler_m": "주인공_3세_남", "p_toddler_f": "주인공_3세_여",
    "p_kinder_m": "주인공_6세_남", "p_kinder_f": "주인공_6세_여", "p_elem_m": "주인공_초등_남", "p_elem_f": "주인공_초등_여",
    "p_mid_m": "주인공_중학생_남", "p_mid_f": "주인공_중학생_여", "p_high_m": "주인공_고등학생_남", "p_high_f": "주인공_고등학생_여",
    "p_univ_m": "주인공_대학생_남", "p_univ_f": "주인공_대학생_여", "p_adult_m": "주인공_성인_남", "p_adult_f": "주인공_성인_여",
    "mom_warm": "엄마_다정", "mom_career": "엄마_커리어", "mom_tired": "엄마_지침",
    "dad_warm": "아빠_다정", "dad_elite": "아빠_엘리트", "dad_worn": "아빠_무기력", "dad_hardware": "아빠_철물점",
    "grandma": "할머니", "grandpa": "할아버지", "sib_baby": "동생_아기", "sib_m": "동생_남", "sib_f": "동생_여",
    "samsin": "삼신할미", "ab_dokkaebi_mom": "비정상_도깨비엄마", "ab_magpie_dad": "비정상_까치아빠", "ab_moon": "비정상_달",
    "ab_shadow": "비정상_그림자아이", "ab_gravity": "비정상_중력아이", "ab_rain": "비정상_비피하는아이", "ab_crows": "비정상_새말아이",
    "f_daycare_m": "친구_어린이집_남", "f_daycare_f": "친구_어린이집_여", "f_kinder_m": "친구_유치원_남", "f_kinder_f": "친구_유치원_여",
    "f_elem_m": "친구_초등_남", "f_elem_f": "친구_초등_여", "f_mid_m": "친구_중학교_남", "f_mid_f": "친구_중학교_여_차서은",
    "f_high_m": "친구_고등학교_남", "f_high_f": "친구_고등학교_여_차서은", "rival_m": "라이벌_남", "rival_f": "라이벌_여",
    "f_univ_m": "친구_대학_남", "f_univ_f": "친구_대학_여", "f_adult_m": "친구_성인_남", "f_adult_f": "친구_성인_여",
    "lover_m": "연인_남", "lover_f": "연인_여",
    "t_daycare": "선생님_어린이집", "t_kinder": "선생님_유치원", "t_elem": "선생님_초등담임", "t_mid": "선생님_중학교담임",
    "t_high": "선생님_고등학교담임", "t_academy": "선생님_학원", "t_pe": "선생님_체육코치", "t_librarian": "선생님_사서",
    "neighbor_grandma": "이웃_옆집할머니", "cvs_staff": "이웃_편의점형", "boss": "직장_상사",
    "s_delivery": "장면_분만실", "s_samsin_room": "장면_삼신할미의방", "s_egg": "장면_알강림",
    "s_home_normal": "장면_집_평범", "s_home_rich": "장면_집_넉넉", "s_home_poor": "장면_집_단칸방",
    "s_daycare": "장면_어린이집", "s_kindergarten": "장면_유치원", "s_elem_class": "장면_초등교실", "s_sports_day": "장면_운동회",
    "s_talent_show": "장면_학예회", "s_mid_class": "장면_중학교교실", "s_study_hall": "장면_야자", "s_suneung": "장면_수능",
    "s_graduation": "장면_졸업식", "s_campus": "장면_대학캠퍼스", "s_one_room": "장면_자취방", "s_office_night": "장면_야근사무실",
    "s_highway": "장면_명절고속도로", "s_hospital": "장면_병실", "s_academy_street": "장면_학원가", "s_cvs_night": "장면_편의점",
    "s_magpie_pole": "장면_전봇대까치", "s_crows": "장면_전깃줄까마귀",
}

ALL = {e[0]: (g, e) for g, es in ENTRIES.items() for e in es}
assert set(ALL) == set(FILES), set(ALL) ^ set(FILES)


def token():
    t = os.environ.get("NOVELAI_TOKEN")
    if not t and os.name == "nt":
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
                t = winreg.QueryValueEx(k, "NOVELAI_TOKEN")[0]
        except OSError:
            pass
    if not t:
        sys.exit("NOVELAI_TOKEN 환경변수가 없음")
    return t.strip()


def headers():
    return {"Authorization": f"Bearer {token()}", "Content-Type": "application/json"}


def anlas():
    r = requests.get("https://image.novelai.net/user/subscription", headers=headers(), timeout=30)
    r.raise_for_status()
    d = r.json()
    s = d.get("trainingStepsLeft", {})
    return d.get("tier"), s.get("fixedTrainingStepsLeft", 0) + s.get("purchasedTrainingSteps", 0)


def payload(a, seed):
    w, h = a["size"]
    center = {"x": 0.5, "y": 0.5}
    chars = [{"prompt": a["character"], "uc": a["character_negative"], "center": center, "enabled": True}] if a["character"] else []
    return {
        "input": a["base"], "model": SETTINGS["model"], "action": "generate",
        "parameters": {
            "params_version": 4, "width": w, "height": h,
            "scale": SETTINGS["scale"], "sampler": SETTINGS["sampler"], "steps": SETTINGS["steps"],
            "n_samples": 1, "seed": seed, "cfg_rescale": SETTINGS["cfg_rescale"], "noise_schedule": SETTINGS["noise_schedule"],
            "ucPreset": 0, "qualityToggle": False, "dynamic_thresholding": False, "sm": False, "sm_dyn": False,
            "legacy": False, "legacy_v3_extend": False, "legacy_uc": False,
            "add_original_image": True, "prefer_brownian": True, "deliberate_euler_ancestral_bug": False, "use_coords": False,
            "negative_prompt": a["negative"],
            "characterPrompts": chars,
            "v4_prompt": {"caption": {"base_caption": a["base"],
                                      "char_captions": [{"char_caption": c["prompt"], "centers": [center]} for c in chars]},
                          "use_coords": False, "use_order": True},
            "v4_negative_prompt": {"caption": {"base_caption": a["negative"],
                                               "char_captions": [{"char_caption": c["uc"], "centers": [center]} for c in chars]},
                                   "legacy_uc": False},
        },
    }


def request_image(p):
    for attempt in range(8):
        try:
            r = requests.post("https://image.novelai.net/ai/generate-image", headers=headers(), json=p, timeout=180)
        except requests.RequestException as e:
            print("  네트워크 오류, 재시도:", type(e).__name__, flush=True)
            time.sleep(5 * (attempt + 1)); continue
        if r.status_code == 429 or (r.status_code >= 500 and attempt < 7):
            time.sleep(8 * (attempt + 1)); continue
        return r
    return r


def decode(content):
    if content[:2] == b"PK":
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            return z.read(z.namelist()[0])
    if content[:4] == b"\x89PNG":
        return content
    raise ValueError("알 수 없는 응답 형식")


def load():
    return json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}


def save(st):
    STATE.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")


def cmd_gen(keys):
    RAW.mkdir(exist_ok=True)
    st = load()
    todo = keys or [k for k in ALL if k not in REUSE and not st.get(k, {}).get("files")]
    tier, a0 = anlas()
    print(f"tier={tier} 시작 anlas={a0} · 생성 {len(todo)}장", flush=True)
    for n, k in enumerate(todo, 1):
        if k in REUSE:
            print(f"{k}: 재사용 항목이라 건너뜀"); continue
        a = assemble(ALL[k][1])
        seed = random.randint(1, 2**32 - 1)
        r = request_image(payload(a, seed))
        if r.status_code != 200:
            print(f"[{n}/{len(todo)}] {k} 실패 {r.status_code}: {r.text[:300]}", flush=True)
            if r.status_code in (401, 402, 403):
                break
            continue
        e = st.setdefault(k, {"files": [], "seeds": []})
        f = RAW / f"{k}_{len(e['files']) + 1}.png"
        f.write_bytes(decode(r.content))
        e["files"].append(f.name); e["seeds"].append(seed); e["pick"] = f.name
        save(st)
        print(f"[{n}/{len(todo)}] {k} → {f.name} seed={seed}", flush=True)
        time.sleep(1.0)
    _, a1 = anlas()
    print(f"끝 anlas={a1} (소모 {a0 - a1})")


def cmd_sheet(keys=None):
    st = load()
    out = RAW / "sheets"
    out.mkdir(exist_ok=True)
    for old in out.glob("*.jpg"):
        old.unlink()
    font = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 20)
    items = [(k, RAW / st[k]["pick"]) for k in ALL if k in st and (not keys or k in keys)]
    items += [(k, p) for k, (p, _) in REUSE.items() if not keys or k in keys]
    port = [x for x in items if ALL[x[0]][1][7] != "scene"]
    land = [x for x in items if ALL[x[0]][1][7] == "scene"]
    for tag, group, cols, (tw, th) in (("p", port, 6, (416, 608)), ("s", land, 4, (608, 416))):
        per = cols * 2
        for n in range(0, len(group), per):
            batch = group[n:n + per]
            sheet = Image.new("RGB", (cols * tw, ((len(batch) + cols - 1) // cols) * th), "black")
            d = ImageDraw.Draw(sheet)
            for i, (k, p) in enumerate(batch):
                im = Image.open(p).convert("RGB")
                im.thumbnail((tw, th))
                x, y = (i % cols) * tw, (i // cols) * th
                sheet.paste(im, (x, y))
                d.rectangle([x, y, x + tw, y + 28], fill=(0, 0, 0))
                d.text((x + 6, y + 2), f"{k}  {FILES[k]}", font=font, fill=(255, 230, 80))
            sheet.save(out / f"{tag}_{n // per:02d}.jpg", quality=85)
    print(f"시트: 인물 {len(port)} · 장면 {len(land)}")


def cmd_final():
    st = load()
    FINAL.mkdir(exist_ok=True)
    for old in FINAL.glob("*.png"):  # 전부 raw/·원본에서 복사한 것이라 지우고 다시 만든다
        old.unlink()
    rows, missing = [], []
    for k, (g, e) in ALL.items():
        if k in REUSE:
            src, note = REUSE[k]
        elif k in st:
            src, note = RAW / st[k]["pick"], f"seed {st[k]['seeds'][st[k]['files'].index(st[k]['pick'])]}"
        else:
            missing.append(k); continue
        dst = FINAL / f"{PREFIX}_{FILES[k]}.png"
        shutil.copy2(src, dst)
        rows.append(f"| {g} | {e[1]} | `{dst.name}` | {note} |")
    idx = ["# 정상 · 이미지 목록", "",
           f"{len(rows)}장. 크랙 이미지 표에서 열은 전부 `{PREFIX}` 하나, 행은 파일 이름의 `{PREFIX}_` 뒷부분이라 빈칸이 없다.", "",
           "| 분류 | 항목 | 파일 | 비고 |", "|---|---|---|---|"] + rows
    (FINAL / "INDEX.md").write_text("\n".join(idx) + "\n", encoding="utf-8")
    print(f"정리 {len(rows)}장 → nai/images/", "· 없음: " + ", ".join(missing) if missing else "")
    preview()


def preview():
    """전체 한눈에 보기: nai/preview.jpg (인물 위, 장면 아래)."""
    font = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 15)
    port = [k for k in ALL if ALL[k][1][7] != "scene"]
    land = [k for k in ALL if ALL[k][1][7] == "scene"]
    W = 2000
    pc, pw = 10, 200; ph = int(pw * 1216 / 832)
    lc, lw = 6, W // 6; lh = int(lw * 832 / 1216)
    prow, lrow = (len(port) + pc - 1) // pc, (len(land) + lc - 1) // lc
    sheet = Image.new("RGB", (W, prow * ph + lrow * lh), "black")
    d = ImageDraw.Draw(sheet)
    cells = [(k, (i % pc) * pw, (i // pc) * ph, pw, ph) for i, k in enumerate(port)]
    cells += [(k, (i % lc) * lw, prow * ph + (i // lc) * lh, lw, lh) for i, k in enumerate(land)]
    for k, x, y, w, h in cells:
        im = Image.open(FINAL / f"{PREFIX}_{FILES[k]}.png").convert("RGB")
        im = im.resize((w, int(im.height * w / im.width)), Image.LANCZOS).crop((0, 0, w, h))
        sheet.paste(im, (x, y))
        d.rectangle([x, y + h - 20, x + w, y + h], fill=(0, 0, 0))
        d.text((x + 4, y + h - 20), FILES[k], font=font, fill=(255, 230, 80))
    sheet.save(HERE / "preview.jpg", quality=82)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    if a[0] == "check": print("tier=%s anlas=%s" % anlas())
    elif a[0] == "gen": cmd_gen(a[1:])
    elif a[0] == "sheet": cmd_sheet(a[1:] or None)
    elif a[0] == "final": cmd_final()
    else: sys.exit(__doc__)
