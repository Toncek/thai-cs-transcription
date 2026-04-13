import json
import random

with open('src/lookup.json', 'r', encoding='utf-8') as f:
    lookup = json.load(f)

items = list(lookup.items())
# Set seed so tests are somewhat deterministic
random.seed(1337)
sampled = random.sample(items, int(len(items) * 0.1))

goldens = [{"thai": k, "phonetic_cs": v} for k, v in sampled]

with open('tests/test_goldens.json', 'w', encoding='utf-8') as f:
    json.dump(goldens, f, ensure_ascii=False, indent=2)

print(f"Saved {len(goldens)} entries to tests/test_goldens.json")
