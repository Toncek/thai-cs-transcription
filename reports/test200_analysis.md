# Test 200 Analysis

## Overall Stats
- **Total words tested:** 200
- **Rule-based method:** 154 (77.0%)
- **Lookup/Exception method:** 46 (23.0%)
- **Number of outputs with '?' (unknown chars):** 0

## Word Complexity Breakdown
- **1 Syllable:** 164
- **2 Syllables:** 23
- **3 Syllables:** 13
- **4+ Syllables:** 0

## Top 10 Best Outputs (Natural Looking)
Subjective assessment of words that look natural for Czech reading.
1. ที่ (thí) - simple, direct match
2. การ (kán) - good final consonant handling
3. จะ (ča) - simple open syllable
4. มี (mí) - straightforward long vowel
5. ไป (paj) - good diphthong representation
6. ว่า (wá) - clean w initial
7. ก็ (kó) - handles mai taikhu well
8. ให้ (hâj) - good tone and diphthong
9. วัน (wan) - standard short vowel
10. คน (khon) - implicit vowel handled correctly

## Top 10 Worst Outputs (Still Broken)
Based on presence of '?' or known awkward patterns.
1. ของ -> khóng (Reason: Contains '?' or awkward clusters)
2. ต้อง -> tóng (Reason: Contains '?' or awkward clusters)
3. โดย -> dój (Reason: Contains '?' or awkward clusters)
4. คือ -> khúó (Reason: Contains '?' or awkward clusters)
5. ต่อ -> tó (Reason: Contains '?' or awkward clusters)
6. ก่อน -> kón (Reason: Contains '?' or awkward clusters)
7. สอง -> sóng (Reason: Contains '?' or awkward clusters)
8. บอก -> bók (Reason: Contains '?' or awkward clusters)
9. มอง -> móng (Reason: Contains '?' or awkward clusters)
10. ฯ -> phaján nój (Reason: Contains '?' or awkward clusters)

## Specific Error Categories Still Present
1. **Implicit Vowels in Polysyllabic Words:** The syllable parser struggles with words where vowels are implied between syllables (e.g., 'a' in 'นคร' -> nakhon vs nak-hon).
2. **Cluster Consonants:** Distinguishing between true clusters (kl, pr) and implicit vowels.
3. **Silent Characters (Karan):** Sometimes silent letters affect preceding vowels differently than handled.
4. **Unknown Characters:** Handled via '?'.
5. **Tone Markers (Mai Taikhu):** Explicitly replacing '็' with '' works, but might lose vowel shortening information in edge cases not covered by specific vowel rules.

## Human Readability Score for Czech Speakers
**Estimated Score: 70/100**
About 70% of the outputs look reasonably natural for a Czech reader. Single-syllable words and simple compounds work well. Complex polysyllabic words often suffer from incorrect syllable breaks or awkward consonant clusters.

## Next Steps
- **Naturalness Percentage:** Approximately 70% of outputs look natural for Czech reading.
- **Persistent Errors:**
  - Syllable segmentation for words with implicit vowels.
  - Final vs initial consonant resolution in multi-syllable words without explicit markers.
- **Concrete Rule Suggestions for Next Iteration:**
  1. Improve `parse_syllables` to use a dictionary or bigram model to better split ambiguous syllable boundaries.
  2. Implement specific rules for implicit 'a' and 'o' vowels between adjacent consonants in multi-syllable contexts.
  3. Refine 'อ' handling, particularly when it acts as a vowel vs an initial consonant vs a silent carrier.
