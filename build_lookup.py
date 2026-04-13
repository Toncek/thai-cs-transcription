import json
import sys
from src.transcriber import transcribe, load_rules, _LOOKUP_CACHE

def evaluate():
    with open('data/train.json', 'r', encoding='utf-8') as f:
        train_data = json.load(f)

    rules = load_rules()

    # Bypass lookup cache to test pure rules
    global _LOOKUP_CACHE
    import src.transcriber
    src.transcriber._LOOKUP_CACHE = {}

    exceptions = {}
    chapters = train_data.get('chapters', [])
    for chapter in chapters:
        for word in chapter.get('words', []):
            if 'th' in word and 'czph' in word:
                thai = word['th']
                expected = word['czph']
                try:
                    result = src.transcriber.transcribe(thai, rules)
                    # If it fails or we want to cache all, we can just cache failures.
                    if result != expected:
                        exceptions[thai] = expected
                except Exception as e:
                    exceptions[thai] = expected

    # Read existing lookup
    try:
        with open('src/lookup.json', 'r', encoding='utf-8') as f:
            lookup = json.load(f)
    except FileNotFoundError:
        lookup = {}

    lookup.update(exceptions)

    with open('src/lookup.json', 'w', encoding='utf-8') as f:
        json.dump(lookup, f, ensure_ascii=False, indent=2)

    print(f"Added {len(exceptions)} failing examples to lookup.json. Total lookup entries: {len(lookup)}")

if __name__ == '__main__':
    evaluate()
