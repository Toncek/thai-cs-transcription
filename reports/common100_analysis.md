# 100 Common Thai Words Analysis

## Overview
This report analyzes the performance of the current Czech-oriented phonetic transcription system on a newly curated dataset of 100 common Thai words.

### Statistics
- **Total words processed:** 100
- **Words transcribed via rules:** 61
- **Words transcribed via lookup:** 39

## Analysis of the Transcription System

### Strengths
- Simple single-syllable words and many lookup words (such as `ผม`, `คุณ`) are handled nicely, producing natural Czech phonetics.
- Basic consonants and final consonants map correctly in straightforward structures (`ฉัน` -> `čan`, `รัก` -> `rak`).

### Recurring Weaknesses and Unnatural Outputs
1. **Silent 'ห' (hó híp) handling:** In words like `หิว` (hungry) or `ใหญ่` (big), the transcriber produces unnatural outputs because it mishandles the leading 'ห' which should just dictate tone or combine with the following consonant, not be explicitly pronounced or mixed up. For example:
   - `หิว` -> `vhi` (incorrect, should be something like `hiu`)
   - `ใหญ่` -> `jajh` (unnatural trailing 'h')
   - `ใหม่` -> `majh` (unnatural trailing 'h')

2. **Compound Vowels & Unnatural Vowel Sequences:**
   - `อะไร` -> `óaraj` (unnatural `óa`)
   - `เก่า` -> `kéá` (unnatural `éá`, should probably be `kao`)
   - `เอา` -> `éóá` (highly unnatural `éóá`, should be `ao`)
   - `เงิน` -> `ngéin` (the standard pronunciation should be closer to `ngön` or `ngün`, `éin` is phonetically odd in Czech)

3. **Character Punctuation in Output:**
   - The system sometimes introduces a question mark (?) for unrecognized or edge case syllables: `เล็ก` -> `lé?k`, `เป็น` -> `pé?n`. This indicates an issue processing the `็` (mai taikhu) character, which shortens the vowel.

4. **Syllable parsing and Initial Consonant clusters:**
   - `อร่อย` -> `rój` (The initial `อ` `ó/a` is dropped, making it missing a syllable).
   - `อย่างไร` -> `jóángraj` (`อ` acting as a silent modifier is misread).
   - `อ่าน` -> `nóá` (completely jumbled consonants and vowels).

### Recommendations for Improvement
1. **Fix `็` (mai taikhu):** Add a rule to handle `็` which typically shortens the vowel. Remove the `?` output and replace it with the correct short vowel equivalent (e.g. `e`).
2. **Improve `ห` leading consonant rules:** Implement logic to recognize when `ห` is a silent tone marker (e.g., before `ง`, `ญ`, `น`, `ม`, `ย`, `ร`, `ล`, `ว`) and when it is an initial consonant.
3. **Refine compound vowels:** Fix the mapping for `เ-า` (which is generating `éá` or `éóá`). It should map directly to `ao`.
4. **Fix Initial `อ`:** Ensure that when `อ` is an initial consonant, it acts as a silent placeholder for the vowel (e.g., `อะไร` -> `araj`, not `óaraj`). Also fix the `อย่า`, `อยู่`, `อย่าง`, `อยาก` exceptions where `อ` is silent before `ย`.
