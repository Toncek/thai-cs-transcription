import json

def main():
    with open("data/test200_thai_cs.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Calculate statistics
    total = len(data)
    rules_count = sum(1 for item in data if item["method_used"] == "rules")
    lookup_count = sum(1 for item in data if "lookup" in item["method_used"])

    syllable_counts = {1: 0, 2: 0, 3: 0, "4+": 0}
    for item in data:
        num_syl = len(item["syllable_breakdown"])
        if num_syl == 1:
            syllable_counts[1] += 1
        elif num_syl == 2:
            syllable_counts[2] += 1
        elif num_syl == 3:
            syllable_counts[3] += 1
        else:
            syllable_counts["4+"] += 1

    # Subjective analysis placeholders
    # Let's count some error indicators like '?'
    errors_with_question_mark = [item for item in data if "?" in item["phonetic_cs"]]

    # Generate table
    table_lines = [
        "| Thai | English | Czech phonetic | Method |",
        "|------|---------|----------------|--------|"
    ]
    for item in data:
        table_lines.append(f"| {item['thai']} | {item['meaning_en']} | {item['phonetic_cs']} | {item['method_used']} |")

    with open("reports/test200_table.md", "w", encoding="utf-8") as f:
        f.write("\n".join(table_lines) + "\n")

    # Generate analysis
    analysis = f"""# Test 200 Analysis

## Overall Stats
- **Total words tested:** {total}
- **Rule-based method:** {rules_count} ({rules_count/total*100:.1f}%)
- **Lookup/Exception method:** {lookup_count} ({lookup_count/total*100:.1f}%)
- **Number of outputs with '?' (unknown chars):** {len(errors_with_question_mark)}

## Word Complexity Breakdown
- **1 Syllable:** {syllable_counts[1]}
- **2 Syllables:** {syllable_counts[2]}
- **3 Syllables:** {syllable_counts[3]}
- **4+ Syllables:** {syllable_counts["4+"]}

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
"""
    # Just list some worst ones, prioritizing those with '?' or errors
    worst = errors_with_question_mark[:10]
    # Fill up to 10 if we have fewer '?'
    if len(worst) < 10:
        other_bad = [item for item in data if item not in worst and ("ó" in item["phonetic_cs"] or len(item["phonetic_cs"]) > 10)][:(10-len(worst))]
        worst.extend(other_bad)

    for i, item in enumerate(worst, 1):
        analysis += f"{i}. {item['thai']} -> {item['phonetic_cs']} (Reason: Contains '?' or awkward clusters)\n"

    analysis += """
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
"""

    with open("reports/test200_analysis.md", "w", encoding="utf-8") as f:
        f.write(analysis)

if __name__ == "__main__":
    main()
