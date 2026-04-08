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
- **Mai taikhu (็)**: This character functions as a vowel-shortening marker. It does not map to any consonant or vowel in Czech output directly, but is removed to avoid emitting invalid characters.
- **Compound vowel เ-า / เอา**: Handled together at the syllable level so `เ` and `า` properly resolve to `ao` instead of being read independently.
- **Initial อ (o ang)**: When `อ` functions as a silent vowel carrier at the beginning of a syllable or before `ย`, it is not pronounced as `ó` if followed by an actual vowel sound. For example, `อะไร` becomes `araj` (not `óaraj`), and `อยู่` becomes `jú` (not `jóú`).
