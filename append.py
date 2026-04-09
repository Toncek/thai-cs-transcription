with open("reports/corpus_analysis.md", "a", encoding="utf-8") as f:
    f.write("""
## D) Error Pattern Analysis
- **Silent consonant leaking into output**:
  - `ราชอาณาจักร` -> `rátánádžakra` (Trailing consonant should be silent or form part of final)
  - `สันสกฤต` -> `sansk?ta` (Trailing `ta` instead of final consonant `t`)
  - `พรมแดน` -> `phrmdén` (Missing implicit vowel between ph and rm, 'พร' usually is 'phr' but 'ม' needs vowel, should be 'phromdén')
- **Compound vowel not recognized / Missing implicit vowel**:
  - `พม่า` -> `phám` (Should be `phamá`, implicit vowel missing for `พ`)
  - `ทฤษฎี` -> `t?tdý` (Character `ฤ` is unhandled, should be `tharuetsadi` -> `tharütsadý`)
  - `อังกฤษ` -> `angk?t` (Character `ฤ` is unhandled, should be `angkryt`)

## E) Comparison with basic vocab
- The system handles basic vocabulary (which often has a 1:1 mapping of consonants to vowels) reasonably well.
- In real-world text from Wikipedia, words are longer, heavily feature Sanskrit/Pali loans (`ราชอาณาจักร`, `ทฤษฎี`, `สันสกฤต`), and use special characters like `ฤ` which the engine lacks fallback logic for.
- Consonant clusters without explicit vowels are failing significantly more frequently in the extended text, often mashing them together or dropping the implicit vowel (e.g. `พม่า` -> `phám` instead of `phamá`).

## F) Human Readability Estimate
- **1-syllable score:** 8/10 (Mostly accurate, direct mappings work well).
- **2-syllable score:** 6/10 (Missing implicit vowels start causing problems, e.g., `พม่า`).
- **3+ syllable score:** 4/10 (Polysyllabic words often fail due to missing vowels, leaking final consonants, or unhandled characters).
- **Overall score:** 5.5/10 (Readable for basic sentences, but struggles with proper nouns and formal terms).

## G) Top 5 Most Interesting Failures
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
""")
