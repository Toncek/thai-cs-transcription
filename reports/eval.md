# Evaluation Report

## Overview
- Total pairs evaluated (held-out gold set): 189
- Correct transcriptions: 17
- Accuracy (Exact match): 8.99%

## Note on Accuracy
The transcriber operates as a pure deterministic rule-based engine parsing Thai strings to Czech phonetics using character/compound string replacement. Thai orthography is highly context-dependent and irregular. We strictly avoided dumping the training set into an exception lookup table, ensuring the rule engine actually executes the logic defined in `spec/rules.json`.

## Failure Analysis
There were 172 failures out of 189 evaluation samples.

### Examples of Failures
- Thai: `บันได`
  - Expected: `bandaj`
  - Actual: `baนajt`
- Thai: `ฬ จฬา`
  - Expected: `drak - hvězda`
  - Actual: `la džán`
- Thai: `ล ลิง`
  - Expected: `opice`
  - Actual: `la ling`
- Thai: `เรอ`
  - Expected: `ré`
  - Actual: `réó`
- Thai: `กระเจี๊ยบ`
  - Expected: `kradžíjap`
  - Actual: `kóaéจíjp`
- Thai: `โกะโตะ`
  - Expected: `koto`
  - Actual: `kóaóat`
- Thai: `วายนํ้ม`
  - Expected: `váj nám`
  - Actual: `vájนํm`
- Thai: `นนทบุรี`
  - Expected: `nonthaburý`
  - Actual: `nนทบuín`
- Thai: `อวน`
  - Expected: `uan`
  - Actual: `vón`
- Thai: `มะเขือมวง`
  - Expected: `makhúa muang`
  - Actual: `maéขúóมuang`

## Recommended Next Steps
- Implement a more sophisticated Thai parser capable of identifying implicit 'a' and 'o' vowels correctly based on syllable structure.
- Build context-aware rules that look ahead to determine final consonant transformations.
