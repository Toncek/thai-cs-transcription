import json
import re

def analyze_results():
    with open("data/corpus_test_results.json", "r", encoding="utf-8") as f:
        results = json.load(f)

    total_words = len(results)

    # Method stats
    lookup_count = sum(1 for r in results if r["method_used"] == "lookup")
    rules_count = sum(1 for r in results if r["method_used"] == "rules")
    exceptions_count = sum(1 for r in results if r["method_used"] == "rules_exception")

    # Unknown chars
    unknown_count = sum(1 for r in results if r["has_unknown_char"])

    # Flags
    double_consonant_issues = sum(1 for r in results if "potential_double_consonant_issue" in r["flags"])

    # Complexity
    complexity = {1: {"count": 0, "examples": []}, 2: {"count": 0, "examples": []}, 3: {"count": 0, "examples": []}, 4: {"count": 0, "examples": []}}

    for r in results:
        s_count = r["syllable_count"]
        tier = s_count if s_count < 4 else 4
        complexity[tier]["count"] += 1
        if len(complexity[tier]["examples"]) < 5:
            complexity[tier]["examples"].append(f"{r['thai']} -> {r['phonetic_cs']}")

    # Character coverage
    # Let's extract all thai characters from the words and see which ones are handled
    # Handled = no "?" in phonetic output for this character.
    # Actually transcriber logs unknown characters. Let's see reports/unknown_chars.md
    unknown_chars = []
    try:
        with open("reports/unknown_chars.md", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("- `"):
                    c = line.split("`")[1]
                    unknown_chars.append(c)
    except FileNotFoundError:
        pass

    # Build report
    report = f"""# Corpus Analysis Report

## A) Overall Statistics
- **Total words processed:** {total_words}
- **Lookup vs Rules breakdown:**
  - Rules: {rules_count}
  - Lookup: {lookup_count}
  - Exceptions: {exceptions_count}
- **Words with unknown characters:** {unknown_count}
- **Words with double-consonant issues detected:** {double_consonant_issues}

## B) Word Complexity Breakdown
- **1-syllable:** {complexity[1]["count"]} words
  - Examples: {', '.join(complexity[1]["examples"])}
- **2-syllable:** {complexity[2]["count"]} words
  - Examples: {', '.join(complexity[2]["examples"])}
- **3-syllable:** {complexity[3]["count"]} words
  - Examples: {', '.join(complexity[3]["examples"])}
- **4+ syllable:** {complexity[4]["count"]} words
  - Examples: {', '.join(complexity[4]["examples"])}

## C) Character Coverage
- The engine logs unhandled characters to `reports/unknown_chars.md`.
- Detected unhandled characters during this run: {', '.join(unknown_chars) if unknown_chars else 'None'}
"""
    with open("reports/corpus_analysis.md", "w", encoding="utf-8") as f:
        f.write(report)

if __name__ == "__main__":
    analyze_results()
