import json
import sys
from pathlib import Path
from src.transcriber import transcribe, load_rules

# Use the old rules for "before" and current for "after"?
# Actually, we can just run it on the first 100 phonetic pairs and generate the markdown content.
# "Add a before/after section to reports/common100_analysis.md."
# Let's just create the file since it doesn't exist.

rules = load_rules()
with open('data/train.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Collect first 100 phonetic pairs
words_100 = []
for chapter in data['chapters']:
    for word in chapter['words']:
        if 'czph' in word:
            words_100.append((word['th'], word['czph']))
        if len(words_100) == 100:
            break
    if len(words_100) == 100:
        break

report_path = Path('reports/common100_analysis.md')

before_text = """# Common 100 Words Analysis

## Before Corrections
The transcriber previously struggled with:
- Unnatural extra "h" in outputs like หิว -> vhi, ใหม่ -> majh
- Missing mai taikhu logic (เล็ก -> lé?k)
- Unnatural i/í after d, t, n, l
- Compound vowel เ-า parsing improperly
- Silent initial อ emitting as "ó" before other vowels

"""

after_text = "## After Corrections\n\nBelow is the output of the first 100 words with the corrected rules engine:\n\n"
after_text += "| Thai | Expected | Actual | Match |\n"
after_text += "|---|---|---|---|\n"

matches = 0
for th, expected in words_100:
    actual = transcribe(th, rules)
    match_str = "✅" if actual == expected else "❌"
    if actual == expected:
        matches += 1
    after_text += f"| {th} | {expected} | {actual} | {match_str} |\n"

after_text += f"\n**Total Matches:** {matches}/100\n"

with open(report_path, 'w', encoding='utf-8') as f:
    f.write(before_text + after_text)

print(f"Report written to {report_path}")
