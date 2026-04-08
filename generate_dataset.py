import json
import time
from deep_translator import GoogleTranslator

# Read the first 250 frequent words
words = []
with open("tnc_freq_head.txt", "r") as f:
    for line in f:
        parts = line.strip().split("\t")
        if len(parts) >= 1:
            words.append(parts[0])

# Filter out non-Thai or punctuation
def is_thai(word):
    return all('\u0e00' <= c <= '\u0e7f' for c in word)

words = [w for w in words if is_thai(w)]

# Try to get 200 words
words = words[:200]

translator = GoogleTranslator(source='th', target='en')
test_set = []

for word in words:
    try:
        meaning = translator.translate(word)
        test_set.append({
            "thai": word,
            "meaning_en": meaning,
            "source_url": "https://github.com/PyThaiNLP/pythainlp/blob/dev/pythainlp/corpus/tnc_freq.txt"
        })
        time.sleep(0.1) # Be nice to the API
    except Exception as e:
        print(f"Error translating {word}: {e}")
        continue

with open("data/test200_thai.json", "w", encoding="utf-8") as f:
    json.dump(test_set, f, ensure_ascii=False, indent=2)

print(f"Generated {len(test_set)} words")
