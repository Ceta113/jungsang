"""정상 — NovelAI(V5) 이미지 프롬프트 라이브러리 생성기.

  python nai/build_nai.py

데이터(ENTRIES)는 이 파일 한 곳에만 있고, 세 가지로 뽑는다.
  nai/nai_prompts.md        읽기용 (항목별 장면·캐릭터 줄만)
  nai/nai_prompts_full.txt  NAI 웹에 바로 붙이는 완성본 (베이스·캐릭터·네거 전부 펼침)
  nai/nai_prompts.json      생성 파이프라인용

화풍·네거티브는 캐릭터_이미지생성/config.py(사용자 프롬프트)를 따른다. 다른 점은 세 가지다.
  - 공통 스타일에서 '-1::censored::'를 뺐다. 아이·학생 캐릭터가 많아서다.
  - 'cinematic lighting, warm lighting'은 공통에서 빼고 항목마다 조명을 따로 적는다(야자·고사장은 차가운 빛이어야 해서).
  - 모든 네거티브에 노출 방지 태그를 넣고, 아이·학생 캐릭터에는 아이용 네거티브를 더한다(체형 태그는 아예 쓰지 않는다).
"""
import json
from pathlib import Path

HERE = Path(__file__).parent

SETTINGS = dict(model="nai-diffusion-5-full", steps=28, scale=7, sampler="k_euler_ancestral",
                cfg_rescale=0, noise_schedule="karras", portrait=[832, 1216], landscape=[1216, 832])

STYLE = (
    "0.5::artist:sangobob::, 0.8::artist:ratatatat74 ::, 1.0::artist:patzzi::, 1.0::artist:wujurana::, "
    "1.0::artist:danimaru::, 1.1::artist:quasarcake::, 1.3::artist:ameya (okemu ame)::, 1.3::artist:wlop::, "
    "1.4::artist:henriiku (ahemaru)::, year 2026, year 2025, year 2024, 3::white outline, colored lineart::, 2::manga::, "
    "ultra complexity, depth of field, highres, best quality, masterpiece, very aesthetic, absurdres, no text, "
    "-3::artist collaboration ::, -2::flat color::, 0.7::jaggy lines::, 1.2::anime coloring::, "
    "0.2::realistic::, -1::thick outlines, muted color, pale color::, -2::people background, crowd background::"
)

NEG = (
    "nsfw, suggestive, revealing clothes, cleavage, swimsuit, underwear, "
    "blank page, text, logo, watermark, too many watermarks, reference, signature, artist name, dated, artistic error, "
    "scan artifacts, jpeg artifacts, upscaled, aliasing, film grain, heavy film grain, dithering, chromatic aberration, "
    "digital dissolve, halftone, screentones, artist:xinzoruo, artist:milkpanda, artist:kurukurumagica, artist collaboration, "
    "one-hour drawing challenge, toon (style), 1990s (style), 4koma, 2koma, mutation, deformed, distorted, disfigured, "
    "bad anatomy, unnatural hair, bad face, mob face, bad eyes, empty eyes, bad proportions, bad limbs, amputee, bad arm, "
    "bad hands, bad hand structure, extra digits, fewer digits, bad leg, extra leg, distorted composition, bad perspective, "
    "multiple views, disorganized colors, unfinished, incomplete, displeasing, very displeasing, unsatisfactory, inadequate, "
    "deficient, subpar, poor, blurry, lowres, worst quality, bad quality, fewer details, sketch, sketch lines, jaggy lines, "
    "rough lines, multiple others, outline, outer glow, white pupils, colored inner hair, saturated"
)

CHAR_NEG = (
    "multiple people, bad proportions, deformed, disfigured, worst quality, bad quality, very displeasing, displeasing, "
    "lowres, error, artistic error, bad anatomy, bad perspective, bad face, bad teeth, bad neck, bad arm, bad hands, "
    "bad leg, bad feet, extra faces, extra eyes, extra eyebrows, extra mouth, extra ears, extra arms, extra hands, "
    "extra legs, extra digits, missing limb, missing finger, wrong hand, mutation, unfinished, jpeg artifacts, "
    "watermark, signature, logo, dark nose, blurry, multiple views, comic, thick eyeliner, heavy makeup, bold lines, "
    "thick outlines"
)
CHILD_NEG = "makeup, lipstick, mature female, mature male, adult, older, revealing clothes, suggestive"

# 표정: 캐릭터 줄 끝의 기본 표정을 이걸로 갈아 끼우면 된다
EXPR = {
    "기본": "light smile, closed mouth, looking at viewer",
    "활짝": "smile, open mouth, happy, looking at viewer",
    "무표정": "expressionless, closed mouth",
    "진지": "serious, closed mouth, looking at viewer",
    "놀람": "surprised, wide eyes, open mouth",
    "부끄러움": "embarrassed, light blush, looking away",
    "화남": "angry, frown, pout",
    "슬픔": "sad, downcast eyes, closed mouth",
    "울음": "crying, tears, open mouth",
    "졸림": "sleepy, half-closed eyes, yawning",
    "지침": "tired, half-closed eyes, slight frown",
    "잠": "sleeping, closed eyes",
}

UNI_MID_M = "korean school uniform, navy blazer, white collared shirt, navy tie, grey pants"
UNI_MID_F = "korean school uniform, navy blazer, white collared shirt, navy ribbon, plaid skirt, black knee socks"
UNI_HIGH_M = "korean school uniform, charcoal grey blazer, white collared shirt, red tie, grey pants"
UNI_HIGH_F = "korean school uniform, charcoal grey blazer, white collared shirt, red ribbon, grey plaid skirt"
MAGPIE = "1.2::magpie, black and white bird, long tail, iridescent blue-green feathers::"

# (키, 한글 이름, 크랙 이미지 키워드 예시, 인원 태그, 캐릭터, 기본 표정, 장면·구도, 종류)  종류: adult / child / scene
ENTRIES = {
    "주인공 ({user}) — 나이별": [
        ("p_baby", "아기 (0세)", "{user}·아기", "solo", "baby, infant, newborn, tiny, chubby cheeks, short black hair, wrapped in white swaddling blanket", "잠", "hospital nursery, bassinet, soft morning light, close-up, from above", "child"),
        ("p_toddler_m", "어린이집 (3세·남)", "{user}·3세", "1boy, solo", "toddler, boy, 1.2::short black hair::, round face, chubby cheeks, dark brown eyes, yellow hoodie, denim overalls, small backpack, name tag", "활짝", "daycare playroom, toys, colorful floor mats, daylight, full body", "child"),
        ("p_toddler_f", "어린이집 (3세·여)", "{user}·3세", "1girl, solo", "toddler, girl, black hair, short pigtails, round face, chubby cheeks, dark brown eyes, pink jacket, leggings, small backpack, name tag", "활짝", "daycare playroom, toys, colorful floor mats, daylight, full body", "child"),
        ("p_kinder_m", "유치원 (6세·남)", "{user}·6세", "1boy, solo", "child, boy, short black hair, dark brown eyes, navy sweatshirt, khaki pants, sneakers, kindergarten bag", "기본", "kindergarten classroom, crayons, drawings on wall, daylight, full body", "child"),
        ("p_kinder_f", "유치원 (6세·여)", "{user}·6세", "1girl, solo", "child, girl, black hair, low twintails, dark brown eyes, yellow cardigan, white blouse, skirt, sneakers, kindergarten bag", "기본", "kindergarten classroom, crayons, drawings on wall, daylight, full body", "child"),
        ("p_elem_m", "초등학생 (10세·남)", "{user}·초등", "1boy, solo", "child, boy, elementary school student, short black hair, messy hair, dark brown eyes, grey hoodie, jeans, school backpack", "기본", "elementary school classroom, wooden desks, blackboard, daylight, cowboy shot", "child"),
        ("p_elem_f", "초등학생 (10세·여)", "{user}·초등", "1girl, solo", "child, girl, elementary school student, black hair, bob cut, dark brown eyes, striped t-shirt, denim skirt, school backpack", "기본", "elementary school classroom, wooden desks, blackboard, daylight, cowboy shot", "child"),
        ("p_mid_m", "중학생 (15세·남)", "{user}·중학생", "1boy, solo", f"teenage, boy, middle school student, black hair, short hair, dark brown eyes, {UNI_MID_M}", "무표정", "middle school classroom, window, daylight, cowboy shot", "child"),
        ("p_mid_f", "중학생 (15세·여)", "{user}·중학생", "1girl, solo", f"teenage, girl, middle school student, black hair, shoulder-length hair, dark brown eyes, {UNI_MID_F}", "무표정", "middle school classroom, window, daylight, cowboy shot", "child"),
        ("p_high_m", "고등학생 (18세·남)", "{user}·고등학생", "1boy, solo", f"teenage, boy, high school student, black hair, short hair, dark brown eyes, {UNI_HIGH_M}", "지침", "classroom at night, self-study, desk lamp, stacked workbooks, cowboy shot", "child"),
        ("p_high_f", "고등학생 (18세·여)", "{user}·고등학생", "1girl, solo", f"teenage, girl, high school student, black hair, long hair, low ponytail, dark brown eyes, {UNI_HIGH_F}", "지침", "classroom at night, self-study, desk lamp, stacked workbooks, cowboy shot", "child"),
        ("p_univ_m", "대학생 (21세·남)", "{user}·대학생", "1boy, solo", "young adult, man, university student, black hair, short hair, dark brown eyes, oversized hoodie, jeans, tote bag", "기본", "university campus, cherry blossoms, spring, daylight, cowboy shot", "adult"),
        ("p_univ_f", "대학생 (21세·여)", "{user}·대학생", "1girl, solo", "young adult, woman, university student, dark brown hair, long hair, dark brown eyes, beige cardigan, white t-shirt, long skirt, tote bag", "기본", "university campus, cherry blossoms, spring, daylight, cowboy shot", "adult"),
        ("p_adult_m", "성인 (30세·남)", "{user}·성인", "1boy, solo", "adult, man, 30s, black hair, short hair, dark brown eyes, white dress shirt, sleeves rolled up, slacks, lanyard", "진지", "office, evening, city view window, cowboy shot", "adult"),
        ("p_adult_f", "성인 (30세·여)", "{user}·성인", "1girl, solo", "adult, woman, 30s, black hair, medium hair, dark brown eyes, white blouse, navy slacks, lanyard", "진지", "office, evening, city view window, cowboy shot", "adult"),
    ],
    "가족": [
        ("mom_warm", "엄마 · 다정 (정상·준수)", "엄마", "1girl, solo", "adult, woman, 30s, mother, dark brown hair, low ponytail, gentle eyes, brown eyes, cream knit sweater, apron", "기본", "home kitchen, morning light, steam from pot, cowboy shot", "adult"),
        ("mom_career", "엄마 · 바쁜 커리어 (희귀·전설)", "엄마", "1girl, solo", "adult, woman, 30s, mother, black hair, neat bob cut, brown eyes, white coat, doctor, stethoscope, id card", "진지", "hospital corridor, bright fluorescent light, cowboy shot", "adult"),
        ("mom_tired", "엄마 · 지친 (실패·재앙)", "엄마", "1girl, solo", "adult, woman, 30s, mother, dark brown hair, messy bun, dark circles, brown eyes, grey zip-up hoodie, holding plastic grocery bag", "지침", "small apartment kitchen, night, single light bulb, cowboy shot", "adult"),
        ("dad_warm", "아빠 · 다정 (정상·준수)", "아빠", "1boy, solo", "adult, man, 30s, father, short black hair, kind eyes, brown eyes, delivery uniform, cap", "활짝", "apartment entrance, evening, delivery boxes, cowboy shot", "adult"),
        ("dad_elite", "아빠 · 엘리트 (희귀·전설)", "아빠", "1boy, solo", "adult, man, 40s, father, black hair, neat side part, glasses, brown eyes, navy suit, necktie, wristwatch", "진지", "study room, bookshelves, evening, warm lighting, cowboy shot", "adult"),
        ("dad_worn", "아빠 · 무기력 (실패·재앙)", "아빠", "1boy, solo", "adult, man, 40s, father, messy black hair, stubble, tired eyes, faded grey t-shirt, old cardigan", "지침", "dim room, night, monitor light, curtains closed, cowboy shot", "adult"),
        ("dad_hardware", "아빠 · 제일 다정한 철물점 사장 (전설)", "아빠", "1boy, solo", "adult, man, 40s, father, short greying hair, kind eyes, laugh lines, work apron, cotton work gloves, holding wrench", "활짝", "small hardware store, shelves of tools, afternoon light, cowboy shot", "adult"),
        ("grandma", "할머니", "할머니", "1girl, solo, old woman", "old woman, elderly, 70s, grandmother, short grey permed hair, kind eyes, wrinkles, floral blouse, knit vest", "기본", "traditional korean house, wooden porch, autumn, persimmon tree, daylight, cowboy shot", "adult"),
        ("grandpa", "할아버지", "할아버지", "1boy, solo, old man", "old man, elderly, 70s, grandfather, short white hair, thick eyebrows, wrinkles, padded vest, holding folded newspaper", "기본", "village pavilion, summer, shade of big tree, daylight, cowboy shot", "adult"),
        ("sib_baby", "동생 · 아기", "동생", "solo", "baby, infant, crawling, chubby cheeks, short black hair, onesie, pacifier", "기본", "apartment living room floor, play mat, afternoon light, full body", "child"),
        ("sib_m", "동생 · 남 (5세)", "동생", "1boy, solo", "child, boy, short black hair, round face, black eyes, dinosaur hoodie, holding toy car", "활짝", "apartment living room, toys on floor, afternoon light, full body", "child"),
        ("sib_f", "동생 · 여 (5세)", "동생", "1girl, solo", "child, girl, black hair, short pigtails, round face, black eyes, rabbit print cardigan, holding stuffed rabbit", "활짝", "apartment living room, toys on floor, afternoon light, full body", "child"),
    ],
    "삼신할미 · 비정상": [
        ("samsin", "삼신할미", "삼신할미", "1girl, solo, old woman", "old woman, elderly, grandmother, white hair, hair bun, 1.2::white hanbok, korean traditional clothes::, round glasses on nose, holding bamboo basket of glowing eggs", "기본", "traditional korean room, wooden shelves full of glowing eggs, candlelight, hearth, steam, warm lighting, cowboy shot", "adult"),
        ("ab_dokkaebi_mom", "도깨비 엄마 (비정상 부모)", "엄마·도깨비", "1girl, solo", "adult, woman, 30s, mother, long black hair, two small horns, golden eyes, cardigan over house dress, blue will-o'-the-wisp floating around", "기본", "apartment living room, night, full moon outside window, blue flame light, cowboy shot", "adult"),
        ("ab_magpie_dad", "까치 아빠 · 사람 모습 (비정상 부모)", "아빠·까치", "1boy, solo", f"adult, man, 30s, father, black hair with white streak, black suit, white shirt, iridescent blue-green necktie, gentle eyes, {MAGPIE} perched on shoulder", "기본", "apartment alley, utility pole, power lines, morning, cowboy shot", "adult"),
        ("ab_moon", "달 (이불을 덮어 주는 달)", "달", "1girl, solo", "moon spirit, personification, ethereal woman, long silver hair, softly glowing skin, crescent moon hair ornament, flowing white robe, floating", "기본", "bedroom at night, open window, moonlight streaming in, blanket, quiet, cowboy shot", "adult"),
        ("ab_shadow", "그림자가 따로 움직이는 아이 (비정상 재능)", "비정상·그림자", "1boy, solo", "child, boy, short black hair, black eyes, school backpack, standing still, 1.3::his shadow waving on its own, detached shadow::", "놀람", "sidewalk, sunset, long shadows, full body", "child"),
        ("ab_gravity", "중력이 절반인 아이 (비정상 재능)", "비정상·중력", "1girl, solo", "child, girl, black hair, bob cut, black eyes, school clothes, 1.3::pencils and books floating around her, hair floating::", "놀람", "elementary school classroom, daylight, full body", "child"),
        ("ab_rain", "비가 피해 가는 아이 (비정상 재능)", "비정상·비", "1boy, solo", "child, boy, short black hair, black eyes, dry clothes, no umbrella, 1.3::rain falling around him but not on him::", "기본", "street, heavy rain, overcast, puddles, full body", "child"),
        ("ab_crows", "새의 말을 알아듣는 아이 (비정상 재능)", "비정상·새", "1girl, solo", "child, girl, black hair, low twintails, black eyes, school backpack, looking up, listening, hand cupped to ear", "놀람", "after school, power lines, 1.2::crows perched on power lines, thick beaks, black feathers::, afternoon, from below", "child"),
    ],
    "친구 — 시기별": [
        ("f_daycare_m", "어린이집 친구 (남)", "어린이집 친구", "1boy, solo", "toddler, boy, dark brown hair, bowl cut, round face, chubby cheeks, black eyes, dinosaur t-shirt, shorts", "활짝", "daycare playroom, building blocks, daylight, full body", "child"),
        ("f_daycare_f", "어린이집 친구 (여)", "어린이집 친구", "1girl, solo", "toddler, girl, black hair, hair bun on top, round face, chubby cheeks, black eyes, strawberry print dress, cardigan", "활짝", "daycare playroom, building blocks, daylight, full body", "child"),
        ("f_kinder_m", "유치원 친구 (남)", "유치원 친구", "1boy, solo", "child, boy, short spiky black hair, black eyes, missing tooth, red sweatshirt, name tag", "활짝", "kindergarten playground, sandbox, slide, daylight, full body", "child"),
        ("f_kinder_f", "유치원 친구 (여)", "유치원 친구", "1girl, solo", "child, girl, dark brown hair, long hair, hairband, black eyes, purple dress, white tights", "기본", "kindergarten playground, sandbox, slide, daylight, full body", "child"),
        ("f_elem_m", "초등학교 친구 (남)", "초등 친구", "1boy, solo", "child, boy, elementary school student, dark brown hair, short hair, bandaid on cheek, black eyes, soccer jersey, shorts, holding soccer ball", "활짝", "school playground, after school, golden hour, full body", "child"),
        ("f_elem_f", "초등학교 친구 (여)", "초등 친구", "1girl, solo", "child, girl, elementary school student, black hair, two side braids, round glasses, black eyes, mint hoodie, holding book", "기본", "school library corner, afternoon light, cowboy shot", "child"),
        ("f_mid_m", "중학교 친구 (남)", "중학교 친구", "1boy, solo", f"teenage, boy, middle school student, short spiky black hair, black eyes, {UNI_MID_M}, open blazer, loose tie, headphones around neck", "활짝", "school hallway, lockers, daylight, cowboy shot", "child"),
        ("f_mid_f", "중학교 친구 (여)", "중학교 친구", "1girl, solo", f"teenage, girl, middle school student, dark brown hair, short hair, hair clip, black eyes, {UNI_MID_F}", "기본", "school hallway, lockers, daylight, cowboy shot", "child"),
        ("f_high_m", "고등학교 친구 (남)", "고등학교 친구", "1boy, solo", f"teenage, boy, high school student, black hair, slightly long hair, black eyes, {UNI_HIGH_M}, white earphones", "졸림", "convenience store at night, cup ramen, cowboy shot", "child"),
        ("f_high_f", "고등학교 친구 (여)", "고등학교 친구", "1girl, solo", f"teenage, girl, high school student, black hair, long straight hair, black eyes, {UNI_HIGH_F}, holding flashcards", "지침", "cram school building at night, fluorescent lights, cowboy shot", "child"),
        ("rival_m", "라이벌 (남·고등)", "라이벌", "1boy, solo", f"teenage, boy, high school student, neat short black hair, sharp eyes, rimless glasses, {UNI_HIGH_M}, holding exam paper", "진지", "classroom after exam, afternoon, cowboy shot", "child"),
        ("rival_f", "라이벌 (여·고등)", "라이벌", "1girl, solo", f"teenage, girl, high school student, long black hair, blunt bangs, sharp eyes, {UNI_HIGH_F}, arms crossed", "진지", "classroom after exam, afternoon, cowboy shot", "child"),
        ("f_univ_m", "대학 친구 (남)", "대학 친구", "1boy, solo", "young adult, man, university student, light brown dyed hair, short hair, brown eyes, denim jacket, white t-shirt, guitar case on back", "활짝", "campus lawn, spring, afternoon, cowboy shot", "adult"),
        ("f_univ_f", "대학 친구 (여)", "대학 친구", "1girl, solo", "young adult, woman, university student, dark brown hair, wavy medium hair, brown eyes, striped shirt, cardigan, holding iced coffee", "기본", "campus cafe, afternoon, window light, cowboy shot", "adult"),
        ("f_adult_m", "성인 친구·동료 (남)", "성인 친구", "1boy, solo", "adult, man, 30s, black hair, short hair, brown eyes, navy knit sweater, chinos, holding paper coffee cup", "기본", "korean street food tent, night, warm light, cowboy shot", "adult"),
        ("f_adult_f", "성인 친구·동료 (여)", "성인 친구", "1girl, solo", "adult, woman, 30s, black hair, long hair, low bun, brown eyes, trench coat, holding paper coffee cup", "기본", "city street, autumn, evening, cowboy shot", "adult"),
        ("lover_m", "연인 (남·성인)", "연인", "1boy, solo", "adult, man, late 20s, black hair, soft wavy hair, gentle eyes, oversized knit sweater", "부끄러움", "han river park, sunset, evening, cowboy shot", "adult"),
        ("lover_f", "연인 (여·성인)", "연인", "1girl, solo", "adult, woman, late 20s, dark brown hair, long wavy hair, gentle eyes, beige coat, scarf", "부끄러움", "han river park, sunset, evening, cowboy shot", "adult"),
    ],
    "선생님 · 동네 어른": [
        ("t_daycare", "어린이집 선생님", "어린이집 선생님", "1girl, solo", "adult, woman, 20s, daycare teacher, dark brown hair, ponytail, gentle eyes, pink apron, name tag", "활짝", "daycare playroom, picture books, daylight, cowboy shot", "adult"),
        ("t_kinder", "유치원 선생님", "유치원 선생님", "1boy, solo", "adult, man, 20s, kindergarten teacher, short black hair, round glasses, gentle eyes, green apron, holding picture book", "활짝", "kindergarten classroom, small chairs, daylight, cowboy shot", "adult"),
        ("t_elem", "초등학교 담임", "초등 담임", "1girl, solo", "adult, woman, 30s, elementary school teacher, black hair, bob cut, kind eyes, cardigan, long skirt, holding attendance book", "기본", "elementary school classroom, blackboard, morning light, cowboy shot", "adult"),
        ("t_mid", "중학교 담임", "중학교 담임", "1boy, solo", "adult, man, 40s, middle school teacher, short black hair, receding hairline, tired eyes, navy polo shirt, holding coffee tumbler", "지침", "teachers office, desks with papers, afternoon, cowboy shot", "adult"),
        ("t_high", "고등학교 담임", "고등학교 담임", "1girl, solo", "adult, woman, 40s, high school teacher, black hair, neat low bun, rimless glasses, black blazer, holding exam papers", "진지", "high school classroom, blackboard with exam schedule, cowboy shot", "adult"),
        ("t_academy", "학원 선생님", "학원 선생님", "1boy, solo", "adult, man, 30s, cram school teacher, messy black hair, dark circles, black hoodie, holding marker", "진지", "cram school classroom, night, whiteboard full of math equations, cowboy shot", "adult"),
        ("t_pe", "체육 선생님 · 코치", "코치", "1boy, solo", "adult, man, 30s, pe teacher, coach, short black hair, tan skin, tracksuit, whistle around neck, holding stopwatch", "활짝", "school track field, sunny, cowboy shot", "adult"),
        ("t_librarian", "사서 선생님", "사서 선생님", "1girl, solo", "adult, woman, 50s, librarian, grey streaked hair, low bun, reading glasses on chain, cardigan, holding book", "기본", "school library, bookshelves, afternoon sunlight, cowboy shot", "adult"),
        ("neighbor_grandma", "옆집 할머니", "옆집 할머니", "1girl, solo, old woman", "old woman, elderly, 70s, short curly grey hair, floral pattern pants, padded vest, holding container of kimchi", "활짝", "apartment hallway, front door, daylight, cowboy shot", "adult"),
        ("cvs_staff", "편의점 알바 형", "편의점 형", "1boy, solo", "young adult, man, 20s, convenience store clerk, dark brown hair, tired smile, convenience store uniform, vest, name tag", "기본", "convenience store counter, night, cowboy shot", "adult"),
        ("boss", "직장 상사", "상사", "1girl, solo", "adult, woman, 40s, manager, short black hair, sharp eyes, grey suit, holding documents", "진지", "office meeting room, daylight, cowboy shot", "adult"),
    ],
    "장면 (인물 없음, 가로)": [
        ("s_delivery", "분만실 새벽", "분만실", "no humans", "", "", "hospital delivery room, dawn, fluorescent light, medical equipment, window with sleet, quiet", "scene"),
        ("s_samsin_room", "삼신할미의 방", "삼신할미의 방", "no humans", "", "", "traditional korean room, wooden shelves full of glowing eggs, candlelight, hearth with pot, steam, bamboo basket, warm lighting", "scene"),
        ("s_egg", "알 강림", "알", "no humans", "", "", "single glowing egg descending from ceiling, light rays, hospital room, dawn, ethereal, magical", "scene"),
        ("s_home_normal", "집 · 평범", "집", "no humans", "", "", "korean apartment living room, sofa, tv, children's drawings on fridge, evening, warm lighting", "scene"),
        ("s_home_rich", "집 · 넉넉 (재력 높음)", "집·넉넉", "no humans", "", "", "luxurious modern house living room, high ceiling, grand piano, large windows, city night view", "scene"),
        ("s_home_poor", "집 · 단칸방 (재력 낮음)", "집·단칸방", "no humans", "", "", "small one-room home, folded bedding on floor, red seizure stickers on furniture, single light bulb, night, rain on window", "scene"),
        ("s_daycare", "어린이집", "어린이집", "no humans", "", "", "daycare playroom, colorful floor mats, toys, small chairs, morning light", "scene"),
        ("s_kindergarten", "유치원", "유치원", "no humans", "", "", "kindergarten classroom, crayons, children's drawings on wall, small tables, daylight", "scene"),
        ("s_elem_class", "초등학교 교실", "초등 교실", "no humans", "", "", "korean elementary school classroom, wooden desks, blackboard, flower pot on windowsill, morning light", "scene"),
        ("s_sports_day", "운동회", "운동회", "no humans", "", "", "school sports day, playground, flag garlands, blue and white team flags, tents, sunny, autumn", "scene"),
        ("s_talent_show", "학예회 강당", "학예회", "no humans", "", "", "school auditorium, stage, curtains, spotlight, rows of chairs, balloons", "scene"),
        ("s_mid_class", "중학교 교실 · 노을", "중학교 교실", "no humans", "", "", "korean middle school classroom, lockers at back, notice board, afternoon, sunset light", "scene"),
        ("s_study_hall", "고등학교 야자", "야자", "no humans", "", "", "korean high school classroom at night, self-study, desk lamps, piles of workbooks, dark windows", "scene"),
        ("s_suneung", "수능 고사장", "수능", "no humans", "", "", "exam hall, november morning, desks with exam papers, wall clock, quiet, cold light", "scene"),
        ("s_graduation", "졸업식 교문", "졸업식", "no humans", "", "", "school gate, graduation day, bouquets wrapped in plastic, winter, light snow", "scene"),
        ("s_campus", "대학 캠퍼스 · 봄", "캠퍼스", "no humans", "", "", "university campus, cherry blossoms, red brick buildings, spring, daylight", "scene"),
        ("s_one_room", "자취방", "자취방", "no humans", "", "", "small one-room apartment, single bed, desk with laptop, instant ramen, night, city lights outside", "scene"),
        ("s_office_night", "야근 사무실", "사무실", "no humans", "", "", "office at night, empty desks, monitors on, city night view, blinds", "scene"),
        ("s_highway", "명절 고속도로", "명절", "no humans", "", "", "highway traffic jam, holiday, car tail lights, sunset, long line of cars", "scene"),
        ("s_hospital", "병실", "병실", "no humans", "", "", "hospital room, bed, iv stand, window, afternoon, quiet", "scene"),
        ("s_academy_street", "학원가 밤거리", "학원가", "no humans", "", "", "cram school district at night, buildings with lit windows, parked bicycles, wet street, fluorescent light", "scene"),
        ("s_cvs_night", "편의점 앞 밤", "편의점", "no humans", "", "", "convenience store at night, exterior, plastic tables outside, light spilling onto street", "scene"),
        ("s_magpie_pole", "전봇대 까치 (까치 아빠 평소 모습)", "아빠·까치(평소)", "no humans", "", "", f"{MAGPIE} perched on utility pole, power lines, apartment complex, morning", "scene"),
        ("s_crows", "전깃줄 까마귀", "까마귀", "no humans", "", "", "1.2::crows perched on power lines, thick beaks, black feathers::, after school, afternoon sky", "scene"),
    ],
}


def assemble(e):
    key, ko, kw, count, char, expr, scene, kind = e
    base = f"{count}, {scene}, {STYLE}"
    if kind == "scene":
        return dict(key=key, name=ko, keyword=kw, size=SETTINGS["landscape"], base=base, negative=NEG,
                    character=None, character_negative=None)
    cneg = CHAR_NEG + (", " + CHILD_NEG if kind == "child" else "")
    return dict(key=key, name=ko, keyword=kw, size=SETTINGS["portrait"], base=base, negative=NEG,
                character=f"{char}, {EXPR[expr]}", character_negative=cneg, expression=expr)


def main():
    flat = [(g, assemble(e)) for g, es in ENTRIES.items() for e in es]
    n = len(flat)

    # 읽기용
    md = [f"# 정상 · NAI 이미지 프롬프트 ({n}종)", "",
          "NovelAI V5 Full 기준. 사용자 config(캐릭터_이미지생성)의 화풍을 그대로 쓴다.", "",
          "## 쓰는 법",
          "- NAI 웹에서는 **베이스 프롬프트** 칸에 `베이스` 줄 + 공통 스타일, **캐릭터 프롬프트**(Character 1)에 `캐릭터` 줄, 캐릭터 네거 칸에 `캐릭터 네거`, 아래 Undesired Content에 공통 네거를 넣는다.",
          "- 전부 펼친 완성본은 `nai_prompts_full.txt`에 있다. 그대로 복사하면 된다.",
          f"- 설정: {SETTINGS['model']} · {SETTINGS['steps']} steps · scale {SETTINGS['scale']} · {SETTINGS['sampler']} · {SETTINGS['noise_schedule']} · 인물 832×1216 / 장면 1216×832",
          "- 표정은 `캐릭터` 줄 끝부분(기본 표정)을 아래 표정표의 태그로 갈아 끼우면 된다.",
          "- **안전**: 모든 네거에 노출 방지 태그가 들어 있고, 아이·학생에는 아이용 네거가 더 붙는다. 아이·학생 캐릭터에는 체형 태그를 넣지 않는다.",
          "- `크랙 키워드`는 크랙 상황 이미지에 붙일 이름 예시다.", "",
          "## 공통 스타일 (베이스 뒤에 붙음)", "```", STYLE, "```",
          "## 공통 네거 (Undesired Content)", "```", NEG, "```",
          "## 캐릭터 네거 (기본)", "```", CHAR_NEG, "```",
          "## 아이·학생용 추가 네거 (캐릭터 네거 뒤에 붙음)", "```", CHILD_NEG, "```",
          "## 표정표", "| 표정 | 태그 |", "|---|---|"]
    md += [f"| {k} | `{v}` |" for k, v in EXPR.items()]
    for g, es in ENTRIES.items():
        md += ["", f"## {g}"]
        for e in es:
            a = assemble(e)
            md += ["", f"### {a['name']} · `{a['key']}`", f"크랙 키워드: `{a['keyword']}` · {a['size'][0]}×{a['size'][1]}"
                   + (f" · 기본 표정 {a['expression']}" if a.get("expression") else ""), "```",
                   f"베이스: {e[3]}, {e[6]}"]
            if a["character"]:
                md += [f"캐릭터: {a['character']}",
                       "캐릭터 네거: 기본" + (" + 아이용" if e[7] == "child" else "")]
            md += ["```"]
    (HERE / "nai_prompts.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    # 완성본
    full = [f"정상 · NAI 프롬프트 완성본 ({n}종) — 칸마다 그대로 복사", ""]
    for g, a in flat:
        full += ["=" * 60, f"[{g}] {a['name']} ({a['key']}) · {a['size'][0]}x{a['size'][1]}", "=" * 60,
                 "■ 베이스 프롬프트", a["base"], ""]
        if a["character"]:
            full += ["■ 캐릭터 프롬프트", a["character"], "", "■ 캐릭터 네거", a["character_negative"], ""]
        full += ["■ Undesired Content", a["negative"], "", ""]
    (HERE / "nai_prompts_full.txt").write_text("\n".join(full), encoding="utf-8")

    # 파이프라인용
    data = dict(settings=SETTINGS, expressions=EXPR, entries=[dict(group=g, **a) for g, a in flat])
    (HERE / "nai_prompts.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{n}종 생성: nai_prompts.md / nai_prompts_full.txt / nai_prompts.json")
    for g, es in ENTRIES.items():
        print(f"  {g}: {len(es)}")


if __name__ == "__main__":
    main()
