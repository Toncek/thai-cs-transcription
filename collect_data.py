import requests
from bs4 import BeautifulSoup
import json
import re
import os

os.makedirs('data', exist_ok=True)

# 1. Fetch Thai Wikipedia
urls = [
    "https://th.wikipedia.org/wiki/ประเทศไทย",
    "https://th.wikipedia.org/wiki/ภาษาไทย"
]

texts = []
natural_paragraphs = []

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

for url in urls:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # Get paragraphs
    paragraphs = soup.find_all('p')
    text = ""
    words_collected = 0

    for p in paragraphs:
        p_text = p.get_text()
        # Clean a bit of citations
        p_text = re.sub(r'\[\d+\]', '', p_text)
        if len(p_text) > 100:
            if not natural_paragraphs:
                sentences = re.split(r'(?<=[.!?])\s+', p_text)
                if len(sentences) >= 5 or len(p_text.split()) > 20: # Thai doesn't have spaces usually, maybe check char length
                    natural_paragraphs.append(p_text)

            text += p_text + "\n"
            if len(text) > 2000: # ~200 words is roughly 1000-2000 chars in Thai
                break

    texts.append(text)

with open('data/wiki_source_raw.txt', 'w', encoding='utf-8') as f:
    f.write("\n\n".join(texts))

if natural_paragraphs:
    with open('data/natural_paragraph.txt', 'w', encoding='utf-8') as f:
        f.write(natural_paragraphs[0])
else:
    # fallback
    with open('data/natural_paragraph.txt', 'w', encoding='utf-8') as f:
        f.write(texts[0][:500])

# 2. Fetch extended frequency wordlist
# Wordmastery is a dynamic site, might be hard to scrape. Let's try PyThaiNLP wordlist from their repo instead if wordmastery fails or we can just fetch from github tnc freq.
# The previous script used tnc_freq_head.txt but let's try scraping wordmastery or github.
try:
    response = requests.get('https://raw.githubusercontent.com/PyThaiNLP/pythainlp/dev/pythainlp/corpus/tnc_freq.txt', timeout=10)
    lines = response.text.split('\n')
    extended_vocab = []

    with open('data/train.json', 'r', encoding='utf-8') as f:
        train_data = json.load(f)
        train_words = set()
        if "chapters" in train_data:
            for chapter in train_data["chapters"]:
                for word in chapter.get("words", []):
                    if "th" in word:
                        train_words.add(word["th"])
        elif isinstance(train_data, list):
            for item in train_data:
                if "thai" in item:
                    train_words.add(item["thai"])
                elif "th" in item:
                    train_words.add(item["th"])

    with open('data/test200_thai.json', 'r', encoding='utf-8') as f:
        test_data = json.load(f)
        test_words = {item['thai'] for item in test_data}

    existing_words = train_words.union(test_words)

    rank = 1
    for line in lines:
        parts = line.strip().split('\t')
        if len(parts) >= 1:
            word = parts[0]
            if len(word) >= 2 and all('\u0e00' <= c <= '\u0e7f' for c in word) and word not in existing_words:
                extended_vocab.append({
                    "thai": word,
                    "meaning_en": "", # Not easy to get without translation API, but we just need Thai
                    "rank": rank,
                    "source_url": "https://raw.githubusercontent.com/PyThaiNLP/pythainlp/dev/pythainlp/corpus/tnc_freq.txt"
                })
                if len(extended_vocab) >= 300:
                    break
            rank += 1
except Exception as e:
    print(f"Error getting extended vocab: {e}")

with open('data/extended_vocab.json', 'w', encoding='utf-8') as f:
    json.dump(extended_vocab, f, ensure_ascii=False, indent=2)

sources = {
    "wikipedia_thailand": "https://th.wikipedia.org/wiki/ประเทศไทย",
    "wikipedia_thai_language": "https://th.wikipedia.org/wiki/ภาษาไทย",
    "extended_vocab": "https://raw.githubusercontent.com/PyThaiNLP/pythainlp/dev/pythainlp/corpus/tnc_freq.txt"
}

with open('data/corpus_sources.json', 'w', encoding='utf-8') as f:
    json.dump(sources, f, ensure_ascii=False, indent=2)

print("Data collection complete.")
