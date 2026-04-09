import json
import sys
import os
from collections import defaultdict

# Ensure src can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from src.transcriber import transcribe, load_rules, parse_syllables, load_lookup
from pythainlp.tokenize import word_tokenize

def get_method_used(thai_word, rules, lookup):
    if thai_word in lookup:
        return "lookup"
    if "exceptions" in rules and thai_word in rules["exceptions"]:
        return "rules_exception"
    return "rules"

def detect_flags(word, phonetic, syllables, rules):
    flags = []

    # 1. Double consonant without implicit vowel
    # Thai double consonants usually need an implicit 'o' or 'a'
    # if it's double consonant the transcriber rule will output bob etc.
    # We can check if phonetics have no vowels or something?
    # For now, let's look at the syllables.

    # Check if a known silent consonant is leaking (์)
    # The engine strips ์ so it shouldn't, but let's see.
    # Actually "flags" just wants us to detect potential issues.
    # Example: tone mark in output (not likely, but maybe)
    if any(c in phonetic for c in ["่", "้", "๊", "๋", "์"]):
        flags.append("thai_mark_leaking")

    # Check if there are consecutive consonants in czech without vowels
    vowels_cs = set("aáeéiíoóuúýyüůö")
    consonants_cs = set("bcčdďfghjklmnňpqrřsštťvwxzž")

    # A bit hard to confidently flag this algorithmically without knowing the exact reading,
    # let's just use placeholder flags or basic checks.
    if "?" in phonetic:
        flags.append("unknown_char")

    # Check double identical consonants in thai without explicit vowel
    import re
    # Match 2 identical thai consonants
    # This is a bit complex. Let's just do a basic check
    for c in word:
        if word.count(c) >= 2 and word.find(c+c) != -1:
            if not any(v in word for v in "เแโใไาิีึืุู็ัำ"):
                flags.append("potential_double_consonant_issue")
                break

    return flags

def main():
    with open("data/corpus_test.json", "r", encoding="utf-8") as f:
        corpus = json.load(f)

    rules = load_rules()
    lookup = load_lookup()

    results = []

    for item in corpus:
        word = item["thai"]
        method = get_method_used(word, rules, lookup)
        syllables = parse_syllables(word)

        has_unknown = False

        try:
            phonetic = transcribe(word, rules)
            has_unknown = "?" in phonetic
        except Exception as e:
            phonetic = f"ERROR: {str(e)}"
            has_unknown = True

        flags = detect_flags(word, phonetic, syllables, rules)

        results.append({
            "thai": word,
            "phonetic_cs": phonetic,
            "method_used": method,
            "syllable_count": len(syllables),
            "has_unknown_char": has_unknown,
            "flags": flags
        })

    with open("data/corpus_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # Transcribe paragraph
    with open("data/natural_paragraph.txt", "r", encoding="utf-8") as f:
        paragraph = f.read()

    # Tokenize preserving spaces/punctuation
    tokens = word_tokenize(paragraph, engine='newmm', keep_whitespace=True)

    out_words = []
    for token in tokens:
        if token.strip() == "":
            out_words.append(token)
            continue
        # if token is punctuation or numbers, transcribe will probably pass it through or ?
        # we can just transcribe it
        try:
            phonetic = transcribe(token, rules)
            out_words.append(phonetic)
        except Exception as e:
            out_words.append(f"[{token}]")

    reading = "".join(out_words)

    report_content = f"""# Paragraph Transcription

## Thai original
{paragraph}

## Czech phonetic reading
{reading}
"""

    os.makedirs("reports", exist_ok=True)
    with open("reports/paragraph_transcription.md", "w", encoding="utf-8") as f:
        f.write(report_content)

if __name__ == "__main__":
    main()
