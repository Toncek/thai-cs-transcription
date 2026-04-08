# AGENTS.md

## Project goal
Build a rule-based transcription system that converts arbitrary Thai script words into a Czech-oriented phonetic transcription readable by a native Czech or Slovak speaker.

This is NOT English romanization. This is NOT standard RTGS output.
Output must follow Czech reading conventions.

## Input
- Training data: `data/train.json`
- Each item is a JSON object with at minimum:
  - `thai`: Thai script word (string)
  - `phonetic_cs`: desired Czech phonetic transcription (string)

## Output
The agent must create and maintain:
- `spec/transcription_rules.md` — human-readable rule specification
- `spec/rules.json` — machine-readable rules
- `spec/edge_cases.md` — ambiguities, conflicts, unresolved patterns
- `src/transcriber.py` — deterministic rule engine in Python
- `tests/test_transcriber.py` — automated tests
- `tests/test_goldens.json` — held-out gold evaluation set (sampled from training data)
- `reports/eval.md` — accuracy report over the gold set

## Czech phonetic conventions
- Long vowels → double the vowel letter (e.g. `aa`, `ii`, `uu`) or use `á`, `í`, `ú`
- Aspiration → do not use `ph`, `th`, `kh` (English style). Use `p`, `t`, `k` for unaspirated and document aspirated separately
- Final consonants → apply Thai final consonant rules (e.g. final ง → `ng`, final บ/ด/ก are unreleased, map to Czech equivalents)
- Silent letters → mark in edge_cases.md, do not output them
- Tones → not represented in output unless training pairs show a consistent pattern
- Short vowels: a, e, i, o, u
- Long vowels: aa, ee, ii, oo, uu (or with diacritics)

## Mai taikhu (็) handling
The character ็ is a vowel shortening marker. It does NOT shorten the vowel in output but signals:
- Short vowel where the vowel would otherwise be long
- Replace any "?" output for ็ with the short vowel form
- Examples:
  - เล็ก -> lek (not lé?k)
  - เป็น -> pen (not pé?n)
  - เห็น -> hen (not néh?)
- Never emit literal "?" for ็ in final output.

## Method the agent must follow
1. Analyze all pairs in `data/train.json`
2. Infer mappings for:
   - Initial consonants (onset)
   - Vowel patterns (short/long, position, compound vowels)
   - Final consonants
   - Silent characters
   - Special clusters and loanwords
   - Mai taikhu ็ handling (short vowel marker, no question marks in output)
3. Write all rules into `spec/transcription_rules.md`
4. Encode rules into `spec/rules.json`
5. Implement `src/transcriber.py` as a deterministic rule engine
6. Sample 10% of pairs as a held-out gold set → `tests/test_goldens.json`
7. Run transcriber against gold set, compute accuracy
8. Write full eval report to `reports/eval.md`
9. Write all unresolved or conflicting examples to `spec/edge_cases.md`

## Hard constraints
- Do NOT produce English-style romanization
- Do NOT modify or overwrite `data/train.json`
- Do NOT silently normalize inconsistencies — always document them in `spec/edge_cases.md`
- Every rule must be traceable to at least 3 training examples
- Rules with fewer than 3 examples go to `spec/edge_cases.md` as unconfirmed
- If a pattern is ambiguous (same Thai input, different Czech outputs), report it as a conflict
- Keep the transcriber deterministic and testable
- All files must be UTF-8 encoded
