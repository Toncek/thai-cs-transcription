import json
import os
import sys

# Add src to pythonpath
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from src.transcriber import transcribe, load_rules, parse_syllables, load_lookup

def get_method_used(thai_word, rules, lookup):
    if thai_word in lookup:
        return "lookup"
    if "exceptions" in rules and thai_word in rules["exceptions"]:
        return "lookup (exception)"
    return "rules"

def main():
    with open("data/test200_thai.json", "r", encoding="utf-8") as f:
        test_words = json.load(f)

    rules = load_rules()
    lookup = load_lookup()

    results = []

    for item in test_words:
        word = item["thai"]
        method = get_method_used(word, rules, lookup)

        # Get syllable breakdown
        syllables = parse_syllables(word)

        # Get transcription
        try:
            transcription = transcribe(word, rules)
        except Exception as e:
            transcription = f"ERROR: {str(e)}"

        result_item = {
            "thai": word,
            "meaning_en": item["meaning_en"],
            "phonetic_cs": transcription,
            "method_used": method,
            "syllable_breakdown": syllables
        }
        results.append(result_item)

    with open("data/test200_thai_cs.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
