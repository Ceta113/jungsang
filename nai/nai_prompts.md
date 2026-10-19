# 정상 · NAI 이미지 프롬프트 (88종)

NovelAI V5 Full 기준. 사용자 config(캐릭터_이미지생성)의 화풍을 그대로 쓴다.

## 쓰는 법
- NAI 웹에서는 **베이스 프롬프트** 칸에 `베이스` 줄 + 공통 스타일, **캐릭터 프롬프트**(Character 1)에 `캐릭터` 줄, 캐릭터 네거 칸에 `캐릭터 네거`, 아래 Undesired Content에 공통 네거를 넣는다.
- 전부 펼친 완성본은 `nai_prompts_full.txt`에 있다. 그대로 복사하면 된다.
- 설정: nai-diffusion-5-full · 28 steps · scale 7 · k_euler_ancestral · karras · 인물 832×1216 / 장면 1216×832
- 표정은 `캐릭터` 줄 끝부분(기본 표정)을 아래 표정표의 태그로 갈아 끼우면 된다.
- **안전**: 모든 네거에 노출 방지 태그가 들어 있고, 아이·학생에는 아이용 네거가 더 붙는다. 아이·학생 캐릭터에는 체형 태그를 넣지 않는다.
- `크랙 키워드`는 크랙 상황 이미지에 붙일 이름 예시다.

## 공통 스타일 (베이스 뒤에 붙음)
```
0.5::artist:sangobob::, 0.8::artist:ratatatat74 ::, 1.0::artist:patzzi::, 1.0::artist:wujurana::, 1.0::artist:danimaru::, 1.1::artist:quasarcake::, 1.3::artist:ameya (okemu ame)::, 1.3::artist:wlop::, 1.4::artist:henriiku (ahemaru)::, year 2026, year 2025, year 2024, 3::white outline, colored lineart::, 2::manga::, ultra complexity, depth of field, highres, best quality, masterpiece, very aesthetic, absurdres, no text, -3::artist collaboration ::, -2::flat color::, 0.7::jaggy lines::, 1.2::anime coloring::, 0.2::realistic::, -1::thick outlines, muted color, pale color::, -2::people background, crowd background::
```
## 공통 네거 (Undesired Content)
```
nsfw, suggestive, revealing clothes, cleavage, swimsuit, underwear, blank page, text, logo, watermark, too many watermarks, reference, signature, artist name, dated, artistic error, scan artifacts, jpeg artifacts, upscaled, aliasing, film grain, heavy film grain, dithering, chromatic aberration, digital dissolve, halftone, screentones, artist:xinzoruo, artist:milkpanda, artist:kurukurumagica, artist collaboration, one-hour drawing challenge, toon (style), 1990s (style), 4koma, 2koma, mutation, deformed, distorted, disfigured, bad anatomy, unnatural hair, bad face, mob face, bad eyes, empty eyes, bad proportions, bad limbs, amputee, bad arm, bad hands, bad hand structure, extra digits, fewer digits, bad leg, extra leg, distorted composition, bad perspective, multiple views, disorganized colors, unfinished, incomplete, displeasing, very displeasing, unsatisfactory, inadequate, deficient, subpar, poor, blurry, lowres, worst quality, bad quality, fewer details, sketch, sketch lines, jaggy lines, rough lines, multiple others, outline, outer glow, white pupils, colored inner hair, saturated
```
## 캐릭터 네거 (기본)
```
multiple people, bad proportions, deformed, disfigured, worst quality, bad quality, very displeasing, displeasing, lowres, error, artistic error, bad anatomy, bad perspective, bad face, bad teeth, bad neck, bad arm, bad hands, bad leg, bad feet, extra faces, extra eyes, extra eyebrows, extra mouth, extra ears, extra arms, extra hands, extra legs, extra digits, missing limb, missing finger, wrong hand, mutation, unfinished, jpeg artifacts, watermark, signature, logo, dark nose, blurry, multiple views, comic, thick eyeliner, heavy makeup, bold lines, thick outlines
```
## 아이·학생용 추가 네거 (캐릭터 네거 뒤에 붙음)
```
makeup, lipstick, mature female, mature male, adult, older, revealing clothes, suggestive
```
## 표정표
| 표정 | 태그 |
|---|---|
| 기본 | `light smile, closed mouth, looking at viewer` |
| 활짝 | `smile, open mouth, happy, looking at viewer` |
| 무표정 | `expressionless, closed mouth` |
| 진지 | `serious, closed mouth, looking at viewer` |
| 놀람 | `surprised, wide eyes, open mouth` |
| 부끄러움 | `embarrassed, light blush, looking away` |
| 화남 | `angry, frown, pout` |
| 슬픔 | `sad, downcast eyes, closed mouth` |
| 울음 | `crying, tears, open mouth` |
| 졸림 | `sleepy, half-closed eyes, yawning` |
| 지침 | `tired, half-closed eyes, slight frown` |
| 잠 | `sleeping, closed eyes` |

## 주인공 ({user}) — 나이별

### 아기 (0세) · `p_baby`
크랙 키워드: `{user}·아기` · 832×1216 · 기본 표정 잠
```
베이스: solo, hospital nursery, bassinet, soft morning light, close-up, from above
캐릭터: baby, infant, newborn, tiny, chubby cheeks, short black hair, wrapped in white swaddling blanket, sleeping, closed eyes
캐릭터 네거: 기본 + 아이용
```

### 어린이집 (3세·남) · `p_toddler_m`
크랙 키워드: `{user}·3세` · 832×1216 · 기본 표정 활짝
```
베이스: 1boy, solo, daycare playroom, toys, colorful floor mats, daylight, full body
캐릭터: toddler, boy, 1.2::short black hair::, round face, chubby cheeks, dark brown eyes, yellow hoodie, denim overalls, small backpack, name tag, smile, open mouth, happy, looking at viewer
캐릭터 네거: 기본 + 아이용
```

### 어린이집 (3세·여) · `p_toddler_f`
크랙 키워드: `{user}·3세` · 832×1216 · 기본 표정 활짝
```
베이스: 1girl, solo, daycare playroom, toys, colorful floor mats, daylight, full body
캐릭터: toddler, girl, black hair, short pigtails, round face, chubby cheeks, dark brown eyes, pink jacket, leggings, small backpack, name tag, smile, open mouth, happy, looking at viewer
캐릭터 네거: 기본 + 아이용
```

### 유치원 (6세·남) · `p_kinder_m`
크랙 키워드: `{user}·6세` · 832×1216 · 기본 표정 기본
```
베이스: 1boy, solo, kindergarten classroom, crayons, drawings on wall, daylight, full body
캐릭터: child, boy, short black hair, dark brown eyes, navy sweatshirt, khaki pants, sneakers, kindergarten bag, light smile, closed mouth, looking at viewer
캐릭터 네거: 기본 + 아이용
```

### 유치원 (6세·여) · `p_kinder_f`
크랙 키워드: `{user}·6세` · 832×1216 · 기본 표정 기본
```
베이스: 1girl, solo, kindergarten classroom, crayons, drawings on wall, daylight, full body
캐릭터: child, girl, black hair, low twintails, dark brown eyes, yellow cardigan, white blouse, skirt, sneakers, kindergarten bag, light smile, closed mouth, looking at viewer
캐릭터 네거: 기본 + 아이용
```

### 초등학생 (10세·남) · `p_elem_m`
크랙 키워드: `{user}·초등` · 832×1216 · 기본 표정 기본
```
베이스: 1boy, solo, elementary school classroom, wooden desks, blackboard, daylight, cowboy shot
캐릭터: child, boy, elementary school student, short black hair, messy hair, dark brown eyes, grey hoodie, jeans, school backpack, light smile, closed mouth, looking at viewer
캐릭터 네거: 기본 + 아이용
```

### 초등학생 (10세·여) · `p_elem_f`
크랙 키워드: `{user}·초등` · 832×1216 · 기본 표정 기본
```
베이스: 1girl, solo, elementary school classroom, wooden desks, blackboard, daylight, cowboy shot
캐릭터: child, girl, elementary school student, black hair, bob cut, dark brown eyes, striped t-shirt, denim skirt, school backpack, light smile, closed mouth, looking at viewer
캐릭터 네거: 기본 + 아이용
```

### 중학생 (15세·남) · `p_mid_m`
크랙 키워드: `{user}·중학생` · 832×1216 · 기본 표정 무표정
```
베이스: 1boy, solo, middle school classroom, window, daylight, cowboy shot
캐릭터: teenage, boy, middle school student, black hair, short hair, dark brown eyes, korean school uniform, navy blazer, white collared shirt, navy tie, grey pants, expressionless, closed mouth
캐릭터 네거: 기본 + 아이용
```

### 중학생 (15세·여) · `p_mid_f`
크랙 키워드: `{user}·중학생` · 832×1216 · 기본 표정 무표정
```
베이스: 1girl, solo, middle school classroom, window, daylight, cowboy shot
캐릭터: teenage, girl, middle school student, black hair, shoulder-length hair, dark brown eyes, korean school uniform, navy blazer, white collared shirt, navy ribbon, plaid skirt, black knee socks, expressionless, closed mouth
캐릭터 네거: 기본 + 아이용
```

### 고등학생 (18세·남) · `p_high_m`
크랙 키워드: `{user}·고등학생` · 832×1216 · 기본 표정 지침
```
베이스: 1boy, solo, classroom at night, self-study, desk lamp, stacked workbooks, cowboy shot
캐릭터: teenage, boy, high school student, black hair, short hair, dark brown eyes, korean school uniform, charcoal grey blazer, white collared shirt, red tie, grey pants, tired, half-closed eyes, slight frown
캐릭터 네거: 기본 + 아이용
```

### 고등학생 (18세·여) · `p_high_f`
크랙 키워드: `{user}·고등학생` · 832×1216 · 기본 표정 지침
```
베이스: 1girl, solo, classroom at night, self-study, desk lamp, stacked workbooks, cowboy shot
캐릭터: teenage, girl, high school student, black hair, long hair, low ponytail, dark brown eyes, korean school uniform, charcoal grey blazer, white collared shirt, red ribbon, grey plaid skirt, tired, half-closed eyes, slight frown
캐릭터 네거: 기본 + 아이용
```

### 대학생 (21세·남) · `p_univ_m`
크랙 키워드: `{user}·대학생` · 832×1216 · 기본 표정 기본
```
베이스: 1boy, solo, university campus, cherry blossoms, spring, daylight, cowboy shot
캐릭터: young adult, man, university student, black hair, short hair, dark brown eyes, oversized hoodie, jeans, tote bag, light smile, closed mouth, looking at viewer
캐릭터 네거: 기본
```

### 대학생 (21세·여) · `p_univ_f`
크랙 키워드: `{user}·대학생` · 832×1216 · 기본 표정 기본
```
베이스: 1girl, solo, university campus, cherry blossoms, spring, daylight, cowboy shot
캐릭터: young adult, woman, university student, dark brown hair, long hair, dark brown eyes, beige cardigan, white t-shirt, long skirt, tote bag, light smile, closed mouth, looking at viewer
캐릭터 네거: 기본
```

### 성인 (30세·남) · `p_adult_m`
크랙 키워드: `{user}·성인` · 832×1216 · 기본 표정 진지
```
베이스: 1boy, solo, office, evening, city view window, cowboy shot
캐릭터: adult, man, 30s, black hair, short hair, dark brown eyes, white dress shirt, sleeves rolled up, slacks, lanyard, serious, closed mouth, looking at viewer
캐릭터 네거: 기본
```

### 성인 (30세·여) · `p_adult_f`
크랙 키워드: `{user}·성인` · 832×1216 · 기본 표정 진지
```
베이스: 1girl, solo, office, evening, city view window, cowboy shot
캐릭터: adult, woman, 30s, black hair, medium hair, dark brown eyes, white blouse, navy slacks, lanyard, serious, closed mouth, looking at viewer
캐릭터 네거: 기본
```

## 가족

### 엄마 · 다정 (정상·준수) · `mom_warm`
크랙 키워드: `엄마` · 832×1216 · 기본 표정 기본
```
베이스: 1girl, solo, home kitchen, morning light, steam from pot, cowboy shot
캐릭터: adult, woman, 30s, mother, dark brown hair, low ponytail, gentle eyes, brown eyes, cream knit sweater, apron, light smile, closed mouth, looking at viewer
캐릭터 네거: 기본
```

### 엄마 · 바쁜 커리어 (희귀·전설) · `mom_career`
크랙 키워드: `엄마` · 832×1216 · 기본 표정 진지
```
베이스: 1girl, solo, hospital corridor, bright fluorescent light, cowboy shot
캐릭터: adult, woman, 30s, mother, black hair, neat bob cut, brown eyes, white coat, doctor, stethoscope, id card, serious, closed mouth, looking at viewer
캐릭터 네거: 기본
```

### 엄마 · 지친 (실패·재앙) · `mom_tired`
크랙 키워드: `엄마` · 832×1216 · 기본 표정 지침
```
베이스: 1girl, solo, small apartment kitchen, night, single light bulb, cowboy shot
캐릭터: adult, woman, 30s, mother, dark brown hair, messy bun, dark circles, brown eyes, grey zip-up hoodie, holding plastic grocery bag, tired, half-closed eyes, slight frown
캐릭터 네거: 기본
```

### 아빠 · 다정 (정상·준수) · `dad_warm`
크랙 키워드: `아빠` · 832×1216 · 기본 표정 활짝
```
베이스: 1boy, solo, apartment entrance, evening, delivery boxes, cowboy shot
캐릭터: adult, man, 30s, father, short black hair, kind eyes, brown eyes, delivery uniform, cap, smile, open mouth, happy, looking at viewer
캐릭터 네거: 기본
```

### 아빠 · 엘리트 (희귀·전설) · `dad_elite`
크랙 키워드: `아빠` · 832×1216 · 기본 표정 진지
```
베이스: 1boy, solo, study room, bookshelves, evening, warm lighting, cowboy shot
캐릭터: adult, man, 40s, father, black hair, neat side part, glasses, brown eyes, navy suit, necktie, wristwatch, serious, closed mouth, looking at viewer
캐릭터 네거: 기본
```

### 아빠 · 무기력 (실패·재앙) · `dad_worn`
크랙 키워드: `아빠` · 832×1216 · 기본 표정 지침
```
베이스: 1boy, solo, dim room, night, monitor light, curtains closed, cowboy shot
캐릭터: adult, man, 40s, father, messy black hair, stubble, tired eyes, faded grey t-shirt, old cardigan, tired, half-closed eyes, slight frown
캐릭터 네거: 기본
```

### 아빠 · 제일 다정한 철물점 사장 (전설) · `dad_hardware`
크랙 키워드: `아빠` · 832×1216 · 기본 표정 활짝
```
베이스: 1boy, solo, small hardware store, shelves of tools, afternoon light, cowboy shot
캐릭터: adult, man, 40s, father, short greying hair, kind eyes, laugh lines, work apron, cotton work gloves, holding wrench, smile, open mouth, happy, looking at viewer
캐릭터 네거: 기본
```

### 할머니 · `grandma`
크랙 키워드: `할머니` · 832×1216 · 기본 표정 기본
```
베이스: 1girl, solo, old woman, traditional korean house, wooden porch, autumn, persimmon tree, daylight, cowboy shot
캐릭터: old woman, elderly, 70s, grandmother, short grey permed hair, kind eyes, wrinkles, floral blouse, knit vest, light smile, closed mouth, looking at viewer
캐릭터 네거: 기본
```

### 할아버지 · `grandpa`
크랙 키워드: `할아버지` · 832×1216 · 기본 표정 기본
```
베이스: 1boy, solo, old man, village pavilion, summer, shade of big tree, daylight, cowboy shot
캐릭터: old man, elderly, 70s, grandfather, short white hair, thick eyebrows, wrinkles, padded vest, holding folded newspaper, light smile, closed mouth, looking at viewer
캐릭터 네거: 기본
```

### 동생 · 아기 · `sib_baby`
크랙 키워드: `동생` · 832×1216 · 기본 표정 기본
```
베이스: solo, apartment living room floor, play mat, afternoon light, full body
캐릭터: baby, infant, crawling, chubby cheeks, short black hair, onesie, pacifier, light smile, closed mouth, looking at viewer
캐릭터 네거: 기본 + 아이용
```

### 동생 · 남 (5세) · `sib_m`
크랙 키워드: `동생` · 832×1216 · 기본 표정 활짝
```
베이스: 1boy, solo, apartment living room, toys on floor, afternoon light, full body
캐릭터: child, boy, short black hair, round face, black eyes, dinosaur hoodie, holding toy car, smile, open mouth, happy, looking at viewer
캐릭터 네거: 기본 + 아이용
```

### 동생 · 여 (5세) · `sib_f`
크랙 키워드: `동생` · 832×1216 · 기본 표정 활짝
```
베이스: 1girl, solo, apartment living room, toys on floor, afternoon light, full body
캐릭터: child, girl, black hair, short pigtails, round face, black eyes, rabbit print cardigan, holding stuffed rabbit, smile, open mouth, happy, looking at viewer
캐릭터 네거: 기본 + 아이용
```

## 삼신할미 · 비정상

### 삼신할미 · `samsin`
크랙 키워드: `삼신할미` · 832×1216 · 기본 표정 기본
```
베이스: 1girl, solo, old woman, traditional korean room, wooden shelves full of glowing eggs, candlelight, hearth, steam, warm lighting, cowboy shot
캐릭터: old woman, elderly, grandmother, white hair, hair bun, 1.2::white hanbok, korean traditional clothes::, round glasses on nose, holding bamboo basket of glowing eggs, light smile, closed mouth, looking at viewer
캐릭터 네거: 기본
```

### 도깨비 엄마 (비정상 부모) · `ab_dokkaebi_mom`
크랙 키워드: `엄마·도깨비` · 832×1216 · 기본 표정 기본
```
베이스: 1girl, solo, apartment living room, night, full moon outside window, blue flame light, cowboy shot
캐릭터: adult, woman, 30s, mother, long black hair, two small horns, golden eyes, cardigan over house dress, blue will-o'-the-wisp floating around, light smile, closed mouth, looking at viewer
캐릭터 네거: 기본
```

### 까치 아빠 · 사람 모습 (비정상 부모) · `ab_magpie_dad`
크랙 키워드: `아빠·까치` · 832×1216 · 기본 표정 기본
```
베이스: 1boy, solo, apartment alley, utility pole, power lines, morning, cowboy shot
캐릭터: adult, man, 30s, father, black hair with white streak, black suit, white shirt, iridescent blue-green necktie, gentle eyes, 1.2::magpie, black and white bird, long tail, iridescent blue-green feathers:: perched on shoulder, light smile, closed mouth, looking at viewer
캐릭터 네거: 기본
```

### 달 (이불을 덮어 주는 달) · `ab_moon`
크랙 키워드: `달` · 832×1216 · 기본 표정 기본
```
베이스: 1girl, solo, bedroom at night, open window, moonlight streaming in, blanket, quiet, cowboy shot
캐릭터: moon spirit, personification, ethereal woman, long silver hair, softly glowing skin, crescent moon hair ornament, flowing white robe, floating, light smile, closed mouth, looking at viewer
캐릭터 네거: 기본
```

### 그림자가 따로 움직이는 아이 (비정상 재능) · `ab_shadow`
크랙 키워드: `비정상·그림자` · 832×1216 · 기본 표정 놀람
```
베이스: 1boy, solo, sidewalk, sunset, long shadows, full body
캐릭터: child, boy, short black hair, black eyes, school backpack, standing still, 1.3::his shadow waving on its own, detached shadow::, surprised, wide eyes, open mouth
캐릭터 네거: 기본 + 아이용
```

### 중력이 절반인 아이 (비정상 재능) · `ab_gravity`
크랙 키워드: `비정상·중력` · 832×1216 · 기본 표정 놀람
```
베이스: 1girl, solo, elementary school classroom, daylight, full body
캐릭터: child, girl, black hair, bob cut, black eyes, school clothes, 1.3::pencils and books floating around her, hair floating::, surprised, wide eyes, open mouth
캐릭터 네거: 기본 + 아이용
```

### 비가 피해 가는 아이 (비정상 재능) · `ab_rain`
크랙 키워드: `비정상·비` · 832×1216 · 기본 표정 기본
```
베이스: 1boy, solo, street, heavy rain, overcast, puddles, full body
캐릭터: child, boy, short black hair, black eyes, dry clothes, no umbrella, 1.3::rain falling around him but not on him::, light smile, closed mouth, looking at viewer
캐릭터 네거: 기본 + 아이용
```

### 새의 말을 알아듣는 아이 (비정상 재능) · `ab_crows`
크랙 키워드: `비정상·새` · 832×1216 · 기본 표정 놀람
```
베이스: 1girl, solo, after school, power lines, 1.2::crows perched on power lines, thick beaks, black feathers::, afternoon, from below
캐릭터: child, girl, black hair, low twintails, black eyes, school backpack, looking up, listening, hand cupped to ear, surprised, wide eyes, open mouth
캐릭터 네거: 기본 + 아이용
```

## 친구 — 시기별

### 어린이집 친구 (남) · `f_daycare_m`
크랙 키워드: `어린이집 친구` · 832×1216 · 기본 표정 활짝
```
베이스: 1boy, solo, daycare playroom, building blocks, daylight, full body
캐릭터: toddler, boy, dark brown hair, bowl cut, round face, chubby cheeks, black eyes, dinosaur t-shirt, shorts, smile, open mouth, happy, looking at viewer
캐릭터 네거: 기본 + 아이용
```

### 어린이집 친구 (여) · `f_daycare_f`
크랙 키워드: `어린이집 친구` · 832×1216 · 기본 표정 활짝
```
베이스: 1girl, solo, daycare playroom, building blocks, daylight, full body
캐릭터: toddler, girl, black hair, hair bun on top, round face, chubby cheeks, black eyes, strawberry print dress, cardigan, smile, open mouth, happy, looking at viewer
캐릭터 네거: 기본 + 아이용
```

### 유치원 친구 (남) · `f_kinder_m`
크랙 키워드: `유치원 친구` · 832×1216 · 기본 표정 활짝
```
베이스: 1boy, solo, kindergarten playground, sandbox, slide, daylight, full body
캐릭터: child, boy, short spiky black hair, black eyes, missing tooth, red sweatshirt, name tag, smile, open mouth, happy, looking at viewer
캐릭터 네거: 기본 + 아이용
```

### 유치원 친구 (여) · `f_kinder_f`
크랙 키워드: `유치원 친구` · 832×1216 · 기본 표정 기본
```
베이스: 1girl, solo, kindergarten playground, sandbox, slide, daylight, full body
캐릭터: child, girl, dark brown hair, long hair, hairband, black eyes, purple dress, white tights, light smile, closed mouth, looking at viewer
캐릭터 네거: 기본 + 아이용
```

### 초등학교 친구 (남) · `f_elem_m`
크랙 키워드: `초등 친구` · 832×1216 · 기본 표정 활짝
```
베이스: 1boy, solo, school playground, after school, golden hour, full body
캐릭터: child, boy, elementary school student, dark brown hair, short hair, bandaid on cheek, black eyes, soccer jersey, shorts, holding soccer ball, smile, open mouth, happy, looking at viewer
캐릭터 네거: 기본 + 아이용
```

### 초등학교 친구 (여) · `f_elem_f`
크랙 키워드: `초등 친구` · 832×1216 · 기본 표정 기본
```
베이스: 1girl, solo, school library corner, afternoon light, cowboy shot
캐릭터: child, girl, elementary school student, black hair, two side braids, round glasses, black eyes, mint hoodie, holding book, light smile, closed mouth, looking at viewer
캐릭터 네거: 기본 + 아이용
```

### 중학교 친구 (남) · `f_mid_m`
크랙 키워드: `중학교 친구` · 832×1216 · 기본 표정 활짝
```
베이스: 1boy, solo, school hallway, lockers, daylight, cowboy shot
캐릭터: teenage, boy, middle school student, short spiky black hair, black eyes, korean school uniform, navy blazer, white collared shirt, navy tie, grey pants, open blazer, loose tie, headphones around neck, smile, open mouth, happy, looking at viewer
캐릭터 네거: 기본 + 아이용
```

### 중학교 친구 (여) · `f_mid_f`
크랙 키워드: `중학교 친구` · 832×1216 · 기본 표정 기본
```
베이스: 1girl, solo, school hallway, lockers, daylight, cowboy shot
캐릭터: teenage, girl, middle school student, dark brown hair, short hair, hair clip, black eyes, korean school uniform, navy blazer, white collared shirt, navy ribbon, plaid skirt, black knee socks, light smile, closed mouth, looking at viewer
캐릭터 네거: 기본 + 아이용
```

### 고등학교 친구 (남) · `f_high_m`
크랙 키워드: `고등학교 친구` · 832×1216 · 기본 표정 졸림
```
베이스: 1boy, solo, convenience store at night, cup ramen, cowboy shot
캐릭터: teenage, boy, high school student, black hair, slightly long hair, black eyes, korean school uniform, charcoal grey blazer, white collared shirt, red tie, grey pants, white earphones, sleepy, half-closed eyes, yawning
캐릭터 네거: 기본 + 아이용
```

### 고등학교 친구 (여) · `f_high_f`
크랙 키워드: `고등학교 친구` · 832×1216 · 기본 표정 지침
```
베이스: 1girl, solo, cram school building at night, fluorescent lights, cowboy shot
캐릭터: teenage, girl, high school student, black hair, long straight hair, black eyes, korean school uniform, charcoal grey blazer, white collared shirt, red ribbon, grey plaid skirt, holding flashcards, tired, half-closed eyes, slight frown
캐릭터 네거: 기본 + 아이용
```

### 라이벌 (남·고등) · `rival_m`
크랙 키워드: `라이벌` · 832×1216 · 기본 표정 진지
```
베이스: 1boy, solo, classroom after exam, afternoon, cowboy shot
캐릭터: teenage, boy, high school student, neat short black hair, sharp eyes, rimless glasses, korean school uniform, charcoal grey blazer, white collared shirt, red tie, grey pants, holding exam paper, serious, closed mouth, looking at viewer
캐릭터 네거: 기본 + 아이용
```

### 라이벌 (여·고등) · `rival_f`
크랙 키워드: `라이벌` · 832×1216 · 기본 표정 진지
```
베이스: 1girl, solo, classroom after exam, afternoon, cowboy shot
캐릭터: teenage, girl, high school student, long black hair, blunt bangs, sharp eyes, korean school uniform, charcoal grey blazer, white collared shirt, red ribbon, grey plaid skirt, arms crossed, serious, closed mouth, looking at viewer
캐릭터 네거: 기본 + 아이용
```

### 대학 친구 (남) · `f_univ_m`
크랙 키워드: `대학 친구` · 832×1216 · 기본 표정 활짝
```
베이스: 1boy, solo, campus lawn, spring, afternoon, cowboy shot
캐릭터: young adult, man, university student, light brown dyed hair, short hair, brown eyes, denim jacket, white t-shirt, guitar case on back, smile, open mouth, happy, looking at viewer
캐릭터 네거: 기본
```

### 대학 친구 (여) · `f_univ_f`
크랙 키워드: `대학 친구` · 832×1216 · 기본 표정 기본
```
베이스: 1girl, solo, campus cafe, afternoon, window light, cowboy shot
캐릭터: young adult, woman, university student, dark brown hair, wavy medium hair, brown eyes, striped shirt, cardigan, holding iced coffee, light smile, closed mouth, looking at viewer
캐릭터 네거: 기본
```

### 성인 친구·동료 (남) · `f_adult_m`
크랙 키워드: `성인 친구` · 832×1216 · 기본 표정 기본
```
베이스: 1boy, solo, korean street food tent, night, warm light, cowboy shot
캐릭터: adult, man, 30s, black hair, short hair, brown eyes, navy knit sweater, chinos, holding paper coffee cup, light smile, closed mouth, looking at viewer
캐릭터 네거: 기본
```

### 성인 친구·동료 (여) · `f_adult_f`
크랙 키워드: `성인 친구` · 832×1216 · 기본 표정 기본
```
베이스: 1girl, solo, city street, autumn, evening, cowboy shot
캐릭터: adult, woman, 30s, black hair, long hair, low bun, brown eyes, trench coat, holding paper coffee cup, light smile, closed mouth, looking at viewer
캐릭터 네거: 기본
```

### 연인 (남·성인) · `lover_m`
크랙 키워드: `연인` · 832×1216 · 기본 표정 부끄러움
```
베이스: 1boy, solo, han river park, sunset, evening, cowboy shot
캐릭터: adult, man, late 20s, black hair, soft wavy hair, gentle eyes, oversized knit sweater, embarrassed, light blush, looking away
캐릭터 네거: 기본
```

### 연인 (여·성인) · `lover_f`
크랙 키워드: `연인` · 832×1216 · 기본 표정 부끄러움
```
베이스: 1girl, solo, han river park, sunset, evening, cowboy shot
캐릭터: adult, woman, late 20s, dark brown hair, long wavy hair, gentle eyes, beige coat, scarf, embarrassed, light blush, looking away
캐릭터 네거: 기본
```

## 선생님 · 동네 어른

### 어린이집 선생님 · `t_daycare`
크랙 키워드: `어린이집 선생님` · 832×1216 · 기본 표정 활짝
```
베이스: 1girl, solo, daycare playroom, picture books, daylight, cowboy shot
캐릭터: adult, woman, 20s, daycare teacher, dark brown hair, ponytail, gentle eyes, pink apron, name tag, smile, open mouth, happy, looking at viewer
캐릭터 네거: 기본
```

### 유치원 선생님 · `t_kinder`
크랙 키워드: `유치원 선생님` · 832×1216 · 기본 표정 활짝
```
베이스: 1boy, solo, kindergarten classroom, small chairs, daylight, cowboy shot
캐릭터: adult, man, 20s, kindergarten teacher, short black hair, round glasses, gentle eyes, green apron, holding picture book, smile, open mouth, happy, looking at viewer
캐릭터 네거: 기본
```

### 초등학교 담임 · `t_elem`
크랙 키워드: `초등 담임` · 832×1216 · 기본 표정 기본
```
베이스: 1girl, solo, elementary school classroom, blackboard, morning light, cowboy shot
캐릭터: adult, woman, 30s, elementary school teacher, black hair, bob cut, kind eyes, cardigan, long skirt, holding attendance book, light smile, closed mouth, looking at viewer
캐릭터 네거: 기본
```

### 중학교 담임 · `t_mid`
크랙 키워드: `중학교 담임` · 832×1216 · 기본 표정 지침
```
베이스: 1boy, solo, teachers office, desks with papers, afternoon, cowboy shot
캐릭터: adult, man, 40s, middle school teacher, short black hair, receding hairline, tired eyes, navy polo shirt, holding coffee tumbler, tired, half-closed eyes, slight frown
캐릭터 네거: 기본
```

### 고등학교 담임 · `t_high`
크랙 키워드: `고등학교 담임` · 832×1216 · 기본 표정 진지
```
베이스: 1girl, solo, high school classroom, blackboard with exam schedule, cowboy shot
캐릭터: adult, woman, 40s, high school teacher, black hair, neat low bun, rimless glasses, black blazer, holding exam papers, serious, closed mouth, looking at viewer
캐릭터 네거: 기본
```

### 학원 선생님 · `t_academy`
크랙 키워드: `학원 선생님` · 832×1216 · 기본 표정 진지
```
베이스: 1boy, solo, cram school classroom, night, whiteboard full of math equations, cowboy shot
캐릭터: adult, man, 30s, cram school teacher, messy black hair, dark circles, black hoodie, holding marker, serious, closed mouth, looking at viewer
캐릭터 네거: 기본
```

### 체육 선생님 · 코치 · `t_pe`
크랙 키워드: `코치` · 832×1216 · 기본 표정 활짝
```
베이스: 1boy, solo, school track field, sunny, cowboy shot
캐릭터: adult, man, 30s, pe teacher, coach, short black hair, tan skin, tracksuit, whistle around neck, holding stopwatch, smile, open mouth, happy, looking at viewer
캐릭터 네거: 기본
```

### 사서 선생님 · `t_librarian`
크랙 키워드: `사서 선생님` · 832×1216 · 기본 표정 기본
```
베이스: 1girl, solo, school library, bookshelves, afternoon sunlight, cowboy shot
캐릭터: adult, woman, 50s, librarian, grey streaked hair, low bun, reading glasses on chain, cardigan, holding book, light smile, closed mouth, looking at viewer
캐릭터 네거: 기본
```

### 옆집 할머니 · `neighbor_grandma`
크랙 키워드: `옆집 할머니` · 832×1216 · 기본 표정 활짝
```
베이스: 1girl, solo, old woman, apartment hallway, front door, daylight, cowboy shot
캐릭터: old woman, elderly, 70s, short curly grey hair, floral pattern pants, padded vest, holding container of kimchi, smile, open mouth, happy, looking at viewer
캐릭터 네거: 기본
```

### 편의점 알바 형 · `cvs_staff`
크랙 키워드: `편의점 형` · 832×1216 · 기본 표정 기본
```
베이스: 1boy, solo, convenience store counter, night, cowboy shot
캐릭터: young adult, man, 20s, convenience store clerk, dark brown hair, tired smile, convenience store uniform, vest, name tag, light smile, closed mouth, looking at viewer
캐릭터 네거: 기본
```

### 직장 상사 · `boss`
크랙 키워드: `상사` · 832×1216 · 기본 표정 진지
```
베이스: 1girl, solo, office meeting room, daylight, cowboy shot
캐릭터: adult, woman, 40s, manager, short black hair, sharp eyes, grey suit, holding documents, serious, closed mouth, looking at viewer
캐릭터 네거: 기본
```

## 장면 (인물 없음, 가로)

### 분만실 새벽 · `s_delivery`
크랙 키워드: `분만실` · 1216×832
```
베이스: no humans, hospital delivery room, dawn, fluorescent light, medical equipment, window with sleet, quiet
```

### 삼신할미의 방 · `s_samsin_room`
크랙 키워드: `삼신할미의 방` · 1216×832
```
베이스: no humans, traditional korean room, wooden shelves full of glowing eggs, candlelight, hearth with pot, steam, bamboo basket, warm lighting
```

### 알 강림 · `s_egg`
크랙 키워드: `알` · 1216×832
```
베이스: no humans, single glowing egg descending from ceiling, light rays, hospital room, dawn, ethereal, magical
```

### 집 · 평범 · `s_home_normal`
크랙 키워드: `집` · 1216×832
```
베이스: no humans, korean apartment living room, sofa, tv, children's drawings on fridge, evening, warm lighting
```

### 집 · 넉넉 (재력 높음) · `s_home_rich`
크랙 키워드: `집·넉넉` · 1216×832
```
베이스: no humans, luxurious modern house living room, high ceiling, grand piano, large windows, city night view
```

### 집 · 단칸방 (재력 낮음) · `s_home_poor`
크랙 키워드: `집·단칸방` · 1216×832
```
베이스: no humans, small one-room home, folded bedding on floor, red seizure stickers on furniture, single light bulb, night, rain on window
```

### 어린이집 · `s_daycare`
크랙 키워드: `어린이집` · 1216×832
```
베이스: no humans, daycare playroom, colorful floor mats, toys, small chairs, morning light
```

### 유치원 · `s_kindergarten`
크랙 키워드: `유치원` · 1216×832
```
베이스: no humans, kindergarten classroom, crayons, children's drawings on wall, small tables, daylight
```

### 초등학교 교실 · `s_elem_class`
크랙 키워드: `초등 교실` · 1216×832
```
베이스: no humans, korean elementary school classroom, wooden desks, blackboard, flower pot on windowsill, morning light
```

### 운동회 · `s_sports_day`
크랙 키워드: `운동회` · 1216×832
```
베이스: no humans, school sports day, playground, flag garlands, blue and white team flags, tents, sunny, autumn
```

### 학예회 강당 · `s_talent_show`
크랙 키워드: `학예회` · 1216×832
```
베이스: no humans, school auditorium, stage, curtains, spotlight, rows of chairs, balloons
```

### 중학교 교실 · 노을 · `s_mid_class`
크랙 키워드: `중학교 교실` · 1216×832
```
베이스: no humans, korean middle school classroom, lockers at back, notice board, afternoon, sunset light
```

### 고등학교 야자 · `s_study_hall`
크랙 키워드: `야자` · 1216×832
```
베이스: no humans, korean high school classroom at night, self-study, desk lamps, piles of workbooks, dark windows
```

### 수능 고사장 · `s_suneung`
크랙 키워드: `수능` · 1216×832
```
베이스: no humans, exam hall, november morning, desks with exam papers, wall clock, quiet, cold light
```

### 졸업식 교문 · `s_graduation`
크랙 키워드: `졸업식` · 1216×832
```
베이스: no humans, school gate, graduation day, bouquets wrapped in plastic, winter, light snow
```

### 대학 캠퍼스 · 봄 · `s_campus`
크랙 키워드: `캠퍼스` · 1216×832
```
베이스: no humans, university campus, cherry blossoms, red brick buildings, spring, daylight
```

### 자취방 · `s_one_room`
크랙 키워드: `자취방` · 1216×832
```
베이스: no humans, small one-room apartment, single bed, desk with laptop, instant ramen, night, city lights outside
```

### 야근 사무실 · `s_office_night`
크랙 키워드: `사무실` · 1216×832
```
베이스: no humans, office at night, empty desks, monitors on, city night view, blinds
```

### 명절 고속도로 · `s_highway`
크랙 키워드: `명절` · 1216×832
```
베이스: no humans, highway traffic jam, holiday, car tail lights, sunset, long line of cars
```

### 병실 · `s_hospital`
크랙 키워드: `병실` · 1216×832
```
베이스: no humans, hospital room, bed, iv stand, window, afternoon, quiet
```

### 학원가 밤거리 · `s_academy_street`
크랙 키워드: `학원가` · 1216×832
```
베이스: no humans, cram school district at night, buildings with lit windows, parked bicycles, wet street, fluorescent light
```

### 편의점 앞 밤 · `s_cvs_night`
크랙 키워드: `편의점` · 1216×832
```
베이스: no humans, convenience store at night, exterior, plastic tables outside, light spilling onto street
```

### 전봇대 까치 (까치 아빠 평소 모습) · `s_magpie_pole`
크랙 키워드: `아빠·까치(평소)` · 1216×832
```
베이스: no humans, 1.2::magpie, black and white bird, long tail, iridescent blue-green feathers:: perched on utility pole, power lines, apartment complex, morning
```

### 전깃줄 까마귀 · `s_crows`
크랙 키워드: `까마귀` · 1216×832
```
베이스: no humans, 1.2::crows perched on power lines, thick beaks, black feathers::, after school, afternoon sky
```
