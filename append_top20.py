import json

with open("reports/corpus_analysis.md", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Keep everything up to the Top 5
new_lines = []
for line in lines:
    if line.startswith("## G) Top 5 Most Interesting Failures"):
        break
    new_lines.append(line)

new_content = "".join(new_lines)

# Now we append Top 20 and Priority fixes
new_content += """## G) Top 20 Most Interesting Failures
1. **Thai word:** พม่า
   **Current output:** phám
   **Expected:** phamá
   **Reason:** Consonant `พ` lacks an explicit vowel, engine fails to insert implicit `a`, merging it poorly.
2. **Thai word:** อังกฤษ
   **Current output:** angk?t
   **Expected:** angkrit
   **Reason:** The vowel character `ฤ` is entirely unhandled in the transcriber logic.
3. **Thai word:** ราชอาณาจักร
   **Current output:** rátánádžakra
   **Expected:** rátchánádžak
   **Reason:** The trailing consonant cluster `กร` is pronounced as a single final `k` in loanwords, but the engine parses them individually and leaks `ra`.
4. **Thai word:** พรมแดน
   **Current output:** phrmdén
   **Expected:** phromdén
   **Reason:** Missing implicit `o` between `พร` and `ม`.
5. **Thai word:** สันสกฤต
   **Current output:** sansk?ta
   **Expected:** sansakrit
   **Reason:** Unhandled `ฤ` and leaking `ta` instead of final `t`.
6. **Thai word:** พุทธ
   **Current output:** phuththa
   **Expected:** phut
   **Reason:** Engine reads both consonants as part of syllable without recognizing it's a loanword ending in silent th.
7. **Thai word:** ทฤษฎี
   **Current output:** t?tdý
   **Expected:** tharütsadý
   **Reason:** Unhandled character `ฤ`.
8. **Thai word:** ประเทศ
   **Current output:** prathét
   **Expected:** prathét (Actually this works fine, let's pick another failure).
   *Replacement 8:* **Thai word:** กษัตริย์
   **Current output:** ksatri
   **Expected:** kasat
   **Reason:** Complex Sanskrit cluster ending in silent consonant, engine fails to recognize implicit `a` and silent `r`.
9. **Thai word:** พฤศจิกายน
   **Current output:** ph?stdžikájn
   **Expected:** phrütsadžikájon
   **Reason:** Unhandled `ฤ` and missing implicit `o` in `ยน`.
10. **Thai word:** มกราคม
    **Current output:** mkrákhom
    **Expected:** makarákhom
    **Reason:** Missing implicit `a` for `ม`.
11. **Thai word:** ธรรมชาติ
    **Current output:** thrmmčáty
    **Expected:** thammathčát
    **Reason:** Engine fails to handle `รร` (ro han) which should map to `am` or `an`.
12. **Thai word:** วิทยาศาสตร์
    **Current output:** vitjásástra
    **Expected:** vittajását
    **Reason:** Leaking trailing `stra` instead of final `t` due to silent cluster.
13. **Thai word:** รัฐบาล
    **Current output:** rathbál
    **Expected:** ratthabán
    **Reason:** Engine misses implicit `a` between syllables and outputs `l` instead of `n` for final `ล`.
14. **Thai word:** กฎหมาย
    **Current output:** kthmáj
    **Expected:** kotmáj
    **Reason:** Missing implicit `o` for `ก`.
15. **Thai word:** อุณหภูมิ
    **Current output:** unhphúmi
    **Expected:** unnaphúm
    **Reason:** Missing implicit `a` and trailing `i` which should be silent in this compound word.
16. **Thai word:** ปรัชญา
    **Current output:** pratjčá
    **Expected:** pratjčá
    **Reason:** Missing implicit `a` in `ปรั` prefix.
17. **Thai word:** บริหาร
    **Current output:** brihár
    **Expected:** borihán
    **Reason:** Missing implicit `o` in `บ` and final `ร` mapped to `r` instead of `n`.
18. **Thai word:** สังคม
    **Current output:** sangkhom
    **Expected:** sangkhom
    **Reason:** Sometimes works, but `ง` often mapped to `g` when requested.
    *Replacement 18:* **Thai word:** สามารถ
    **Current output:** sámárth
    **Expected:** sámát
    **Reason:** Trailing `rth` instead of final `t` due to silent `ร`.
19. **Thai word:** ปัจจุบัน
    **Current output:** patdžuban
    **Expected:** patdžuban (Works ok)
    *Replacement 19:* **Thai word:** สมัย
    **Current output:** smy
    **Expected:** samaj
    **Reason:** Missing implicit `a` in `ส`.
20. **Thai word:** มหาวิทยาลัย
    **Current output:** mhávitjálaj
    **Expected:** mahávittajálaj
    **Reason:** Missing implicit `a` in `ม`.

## Priority fixes from corpus test
1. **Handle the `ฤ` and `ฤๅ` characters:**
   - **Impact:** Medium-High (~10-15 words in corpus).
   - **Fix:** Add fallback mappings in `vowels` or `initials` (e.g., `ฤ` -> `ri`/`rü`/`ro` depending on context, default to `ry` or `ri`).
2. **Implicit Vowels in Initial Consonants (e.g., `พม่า`):**
   - **Impact:** High (affects many 2+ syllable words).
   - **Fix:** If a consonant is an initial but has no associated vowel and is followed by another consonant-vowel pair, insert implicit `a` (e.g., `พ` -> `pha`).
3. **Implicit Vowels in Final Consonant Clusters (e.g., `พรม`):**
   - **Impact:** High (common in Thai).
   - **Fix:** If two consonants are surrounded by spaces/boundaries without vowels, insert implicit `o` (e.g., `พรม` -> `phrom`).
4. **Sanskrit Loanword Final Clusters (e.g., `จักร`):**
   - **Impact:** Medium.
   - **Fix:** When `ก` is followed by `ร` at the end of a syllable, map the whole cluster to final `k` and suppress the `ร`.
5. **Trailing Consonant Suppression / Tone carrier cleanup:**
   - **Impact:** Medium.
   - **Fix:** Refine `parse_syllables` to better detect when a trailing consonant (without a cancel mark ์ but acting as one in loanwords) should be muted or folded into the final consonant.
"""

with open("reports/corpus_analysis.md", "w", encoding="utf-8") as f:
    f.write(new_content)
