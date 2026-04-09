import json
import re
from pythainlp.tokenize import word_tokenize

def is_valid_thai_word(word):
    # Strip punctuation, numbers, romanized text, non-Thai chars
    # Allowed Thai chars range \u0e00-\u0e7f
    if len(word) < 2:
        return False
    if not all('\u0e00' <= c <= '\u0e7f' for c in word):
        return False
    return True

# 1. Tokenize wiki source
with open('data/wiki_source_raw.txt', 'r', encoding='utf-8') as f:
    text = f.read()

tokens = word_tokenize(text, engine='newmm')
wiki_words_set = set()
wiki_words_list = []

for token in tokens:
    token = token.strip()
    if is_valid_thai_word(token) and token not in wiki_words_set:
        wiki_words_set.add(token)
        wiki_words_list.append({
            "thai": token,
            "source": "wikipedia"
        })

with open('data/wiki_words.json', 'w', encoding='utf-8') as f:
    json.dump(wiki_words_list, f, ensure_ascii=False, indent=2)

# 2. Merge with extended vocab
with open('data/extended_vocab.json', 'r', encoding='utf-8') as f:
    extended_vocab = json.load(f)

# Load train and test sets to avoid leakage
existing_words = set()

# Get train words
with open('data/train.json', 'r', encoding='utf-8') as f:
    train_data = json.load(f)
    if "chapters" in train_data:
        for chapter in train_data["chapters"]:
            for word in chapter.get("words", []):
                if "th" in word:
                    existing_words.add(word["th"])
    elif isinstance(train_data, list):
        for item in train_data:
            if "thai" in item:
                existing_words.add(item["thai"])
            elif "th" in item:
                existing_words.add(item["th"])

# Get test200 words
with open('data/test200_thai.json', 'r', encoding='utf-8') as f:
    test_data = json.load(f)
    for item in test_data:
        existing_words.add(item["thai"])

corpus_test = []
corpus_words = set()

for item in wiki_words_list:
    word = item["thai"]
    if word not in existing_words and word not in corpus_words:
        corpus_words.add(word)
        corpus_test.append(item)
        if len(corpus_test) >= 300: # try to balance sources
            break

for item in extended_vocab:
    word = item["thai"]
    if word not in existing_words and word not in corpus_words:
        corpus_words.add(word)
        corpus_test.append({
            "thai": word,
            "source": "extended_vocab",
            "meaning_en": item.get("meaning_en", "")
        })
        if len(corpus_test) >= 600:
            break

with open('data/corpus_test.json', 'w', encoding='utf-8') as f:
    json.dump(corpus_test, f, ensure_ascii=False, indent=2)

print(f"Prepared corpus_test.json with {len(corpus_test)} words.")
