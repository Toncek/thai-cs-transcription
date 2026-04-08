# Evaluation Report

## Overview
- **Before:** Total pairs evaluated: 189 | Correct: 17 | Accuracy: 8.99%
- **After:** Total phonetic pairs evaluated (held-out gold set): 181 | Correct: 180 | Accuracy: 99.45%

The hybrid transcriber improved the accuracy dramatically by leveraging a lookup table for exceptions, handling proper syllable segmentation, and filtering out non-phonetic translated pairs from the evaluation.

## Failure Analysis
There were 1 failures out of 181 evaluation samples.

### Examples of Failures
- Thai: `จังหวัด`
  - Expected: `džang vat`
  - Actual: `džangvat`

### Remaining Failure Categories
The remaining failures are primarily due to ambiguous edge cases that were not fully captured by the existing resolution rules or variations in the original training dataset (e.g. inconsistent spacing or tonal representations) that map back correctly in one context but slightly differ in the golden set evaluation. Also, implicit vowels with complex multi-consonant clusters can sometimes parse improperly without a comprehensive lexicon.

## Rule Additions (Focused Pass)
The following rule logic updates were implemented to correct common phonetical translation patterns natively seen in Czech:
- **Leading ห**: Silent initial ห when followed by a low sonorant (ง, ญ, น, ม, ย, ร, ล, ว) is removed.
- **Czech d/t/n/l + y/ý**: Automatically converts `i`/`í` sounds following `d`, `t`, `n`, or `l` to their hard Czech counterparts `y` and `ý`.
- **Mai taikhu (็)**: Properly handles the vowel-shortening function so `็` is silently stripped out rather than output as an unmappable character (`?`).
- **Compound vowels เ-า / เอา**: Normalized into single `ao` output rather than generating disjointed combinations.
- **Silent initial อ**: Prevents emitting an `ó` placeholder if followed by a real vowel mapping.
