# Edge Cases and Conflicts

## Conflicts
- `ใต` maps to multiple outputs: ['taj', 'táj'] -> Resolved to `táj` (tonal, pick with diacritic)
- `จังหวัด` maps to multiple outputs: ['džang vat', 'džangvat'] -> Resolved to `džangvat` (whitespace, pick no space)
- `ทางดวน` maps to multiple outputs: ['tháng dúan', 'tháng duan'] -> Resolved to `tháng dúan` (tonal, pick diacritic)
- `พูกัน` maps to multiple outputs: ['phúkan', 'phú kan'] -> Resolved to `phúkan` (whitespace, pick no space)
- `เสาอากาศ` maps to multiple outputs: ['sáu ákát', 'sau ákát'] -> Resolved to `sáu ákát` (tonal, pick diacritic)
- `ที่เขี่ยบุหรี่` maps to multiple outputs: ['thýkhyja burý', 'thý khyja burý'] -> Resolved to `thýkhyja burý` (whitespace, pick no space)
- `ชั้นวางของ` maps to multiple outputs: ['čán váng khóng', 'čan váng khóng'] -> Resolved to `čán váng khóng` (tonal, pick diacritic)
- `โตะ` maps to multiple outputs: ['to', 'tó'] -> Resolved to `tó` (tonal, pick diacritic)
- `นํ้าสมสายช ู` maps to multiple outputs: ['nám som sáj čú', 'nám som sájčú'] -> Resolved to `nám som sájčú` (whitespace, pick no space)
- `ขวดเกลือ` maps to multiple outputs: ['khúat klúa', 'khuat klúa'] -> Resolved to `khúat klúa` (tonal, pick diacritic)
- `ขวดพริกไทย` maps to multiple outputs: ['khuat phryk thaj', 'khúat phryk thaj'] -> Resolved to `khúat phryk thaj` (tonal, pick diacritic)
- `กลองทิชชู` maps to multiple outputs: ['klóng thytčú', 'klóng thyt čú'] -> Resolved to `klóng thytčú` (whitespace, pick no space)
- `ถังนํ้า` maps to multiple outputs: ['thang nám', 'tháng nám'] -> Resolved to `tháng nám` (tonal, pick diacritic)
- `นางพยาบาล` maps to multiple outputs: ['náng phajábán', 'náng pha já bán'] -> Resolved to `náng phajábán` (whitespace, pick no space)
- `โรงพยาบาล` maps to multiple outputs: ['róng phajábán', 'róng pha já bán'] -> Resolved to `róng phajábán` (whitespace, pick no space)
- `รถพยาบาล` maps to multiple outputs: ['rot phajábán', 'rot pha já bán'] -> Resolved to `rot phajábán` (whitespace, pick no space)
- `การรักษาพยาบาล` maps to multiple outputs: ['kánraksá phajábán', 'kán raksá phajábán'] -> Resolved to `kánraksá phajábán` (whitespace, pick no space)
- `เขา` maps to multiple outputs: ['khao', 'khau'] -> Resolved to `khao` (khao chosen as dominant default)
- `เปด` maps to multiple outputs: ['pet', 'pét'] -> Resolved to `pét` (tonal, pick diacritic)
- `คันเรง` maps to multiple outputs: ['khanreng', 'khan reng'] -> Resolved to `khanreng` (whitespace, pick no space)
- `อ` maps to multiple outputs: ['máj trý', 'máj džat tavá', 'máj thó', 'ó', 'máj ék', 'káran'] -> Resolved to `ó` (default phoneme)

## Unconfirmed exceptions (< 3 occurrences)
The majority of the training set consists of words appearing 1 or 2 times. They fail the strict 3-example threshold for exceptions. They are mapped into the lookup table instead.

## Structural and Pattern Clarifications
- **Mai taikhu (็)**: Treated as a vowel-shortening marker; discarded explicitly during parsing to avoid generating invalid output markers.
- **Leading ห suppression**: Orthographic tone modifier removed directly during parsing if followed by `ง`, `ญ`, `น`, `ม`, `ย`, `ร`, `ล`, or `ว`.
- **Silent initial อ vs. Implicit 'a'**: Avoids emitting `ó` if followed by a vowel, matching phonetic pronunciation instead of orthographic rendering. If `อ` acts as a prefix before another initial consonant without explicit vowels (e.g. `อร่อย`), it is resolved to the implicit vowel `a` (e.g. `arój`) while single carrier usage (e.g. `อ่าน`) drops it (`án`).
- **Compound เ-า vs. เอา**: Both now correctly parse directly as `ao` due to syllable-level normalization.
