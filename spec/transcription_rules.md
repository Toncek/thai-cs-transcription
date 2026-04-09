# Thai → Czech Phonetic Transcription Rules

*This file will be populated by the Jules agent after analysis of data/train.json.*

## Structure
- Section 1: Initial consonants
- Section 2: Vowel patterns
- Section 3: Final consonants
- Section 4: Silent letters
- Section 5: Special cases

## Czech-specific normalizations
- **d, t, n, l + i/í normalization**: After the consonants `d`, `t`, `n`, `l` (which natively soften `i` to `ď, ť, ň` or change pronunciation in Czech), Thai phonetics are usually hard. Therefore, any short `i` or long `í` following these consonants is normalized to `y` and `ý` respectively to preserve the hard pronunciation appropriate for Thai loanwords.
- **Leading ห suppression**: If `ห` (ho hip) appears at the start of a syllable as a tone-class modifier and is followed immediately by a low sonorant (`ง`, `ญ`, `น`, `ม`, `ย`, `ร`, `ล`, `ว`), it is not pronounced and should be completely removed from the phonetic output.
- **Mai taikhu (็)**: This character functions as a vowel-shortening marker. When it is present in a syllable, the vowel output must be converted to its SHORT form (e.g., `á` -> `a`, `é` -> `e`, `í` -> `i`, `ó` -> `o`, `ú` -> `u`, `ý` -> `y`).
- **Compound vowel เ-า / เอา and เ-ิ**: Handled together at the syllable level so `เ` and `า` properly resolve to `ao` instead of being read independently. `เ-ิ` combinations (like in `เงิน`) are normalized to a single vowel sound (e.g., `ö` -> `ngön`).
- **Compound vowel เ-ีย**: This compound vowel explicitly maps to `ia` (e.g., `เสีย` -> `sia`, `เขียน` -> `khian`).
- **Compound vowel ือ**: This compound vowel explicitly maps to the Czech `ü` (e.g., `คือ` -> `khü`).
- **Initial อ (o ang)**: When `อ` functions as a silent vowel carrier at the beginning of a syllable or before `ย`, it is not pronounced as `ó` if followed by an actual vowel sound. For example, `อะไร` becomes `araj` (not `óaraj`), and `อยู่` becomes `jú` (not `jóú`). When `อ` precedes a consonant without an explicit vowel marking, it can act as an unwritten short `a` prefix (e.g. `อร่อย` -> `arój`).
- **Double consonants**: When the same consonant appears twice in a row in the Thai script (e.g., `บบ`, `รร`), it implies an implicit `o` between them and both outputs map to the initial consonant sound (e.g., `ระบบ` -> `rabob`).
- **Thai (ไทย) deduplication**: When the vowel already encodes a `j` sound (like from `ไ` mapping to `aj`), the final `ย` does not emit an extra `j`. Thus, `ไทย` becomes `thaj` or `taj` (based on `ท` mapping) and not `thajj`.
- **Initial ท preference**: `ท` always maps to `t` instead of `th` to better align with user preferences for Czech readers (e.g., `ทำงาน` -> `tamgán`, `ทำให้` -> `tamhaj`).
- **Initial ง preference**: `ง` maps to `g` when functioning as the initial consonant of a syllable instead of `ng`, as `ng` is unnatural for a Czech reader at the start of a syllable (e.g., `ทำงาน` -> `tamgán`).
- **ฎ consonant**: `ฎ` maps to `d` as an initial consonant, and `t` as a final consonant (e.g., `กฎหมาย` -> `kotmáj`).
