import json
import sys
from src.transcriber import transcribe, load_rules, _LOOKUP_CACHE

def evaluate():
    with open('data/train.json', 'r', encoding='utf-8') as f:
        train_data = json.load(f)

    rules = load_rules()

    total = 0
    correct = 0
    failed = []

    chapters = train_data.get('chapters', [])
    for chapter in chapters:
        for word in chapter.get('words', []):
            if 'th' in word and 'czph' in word:
                thai = word['th']
                expected = word['czph']
                total += 1
                try:
                    import src.transcriber as t
                    result = t.transcribe(thai, rules)
                    if result == expected:
                        correct += 1
                    else:
                        failed.append((thai, expected, result))
                except Exception as e:
                    failed.append((thai, expected, f"ERROR: {e}"))

    print(f"Total: {total}")
    print(f"Correct: {correct}")
    print(f"Accuracy: {correct/total*100:.2f}%")

if __name__ == '__main__':
    evaluate()
