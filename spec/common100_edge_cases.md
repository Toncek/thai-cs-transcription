# 100 Common Thai Words - Edge Cases

The following words generated suspicious, incorrect, or unnatural Czech phonetic transcriptions during the 100-word evaluation. These highlight limitations in the current rules engine:

- `เล็ก` -> `lé?k` (Missing rule for `็` mai taikhu)
- `เป็น` -> `pé?n` (Missing rule for `็` mai taikhu)
- `เห็น` -> `néh?` (Misinterpreted `ห` and missing `็` rule)
- `หิว` -> `vhi` (Misinterpreted `ห` and compound vowel rules)
- `ใหญ่` -> `jajh` (Trailing 'h', misinterpreting silent `ห` modifier)
- `ใหม่` -> `majh` (Trailing 'h', misinterpreting silent `ห` modifier)
- `อะไร` -> `óaraj` (`อ` should be silent 'a', not `óa`)
- `เก่า` -> `kéá` (`เ-า` should map to `ao`, not `éá`)
- `เอา` -> `éóá` (`เ-า` with initial `อ` generates extremely unnatural `éóá`)
- `เงิน` -> `ngéin` (Unnatural vowel sequence for Czech)
- `อร่อย` -> `rój` (Dropped the initial `อ` syllable entirely)
- `อย่างไร` -> `jóángraj` (`อ` acting as a silent modifier misread)
- `อ่าน` -> `nóá` (Jumbled logic for `อ` initial and vowels)
- `ที่นั่น` -> `thý nan` (Lookup output has strange spacing and `ý`)

These edge cases should be used as test fixtures to improve the transcription rules in `src/transcriber.py`.
