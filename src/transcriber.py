import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def load_rules(rules_path=None):
    if rules_path is None:
        rules_path = Path(__file__).parent.parent / "spec" / "rules.json"
    with open(rules_path, "r", encoding="utf-8") as f:
        return json.load(f)

_LOOKUP_CACHE = None

def load_lookup(lookup_path=None):
    global _LOOKUP_CACHE
    if _LOOKUP_CACHE is not None:
        return _LOOKUP_CACHE
    if lookup_path is None:
        lookup_path = Path(__file__).parent / "lookup.json"
    if not lookup_path.exists():
        _LOOKUP_CACHE = {}
        return _LOOKUP_CACHE
    with open(lookup_path, "r", encoding="utf-8") as f:
        _LOOKUP_CACHE = json.load(f)
    return _LOOKUP_CACHE

def _log_unknown(char):
    unknown_path = Path(__file__).parent.parent / "reports" / "unknown_chars.md"
    unknown_path.parent.mkdir(parents=True, exist_ok=True)

    if not unknown_path.exists():
        with open(unknown_path, "w", encoding="utf-8") as f:
            f.write("# Unknown Characters\n\n")

    with open(unknown_path, "r", encoding="utf-8") as f:
        content = f.read()

    if f"- `{char}`" not in content:
        with open(unknown_path, "a", encoding="utf-8") as f:
            f.write(f"- `{char}`\n")

LEADING_VOWELS = set("เแโใไ")
FOLLOWING_VOWELS = set("าิีึืุู็ั")
TONE_MARKS = set("่้๊๋")
SILENT_MARK = "์"

CONSONANTS = set([chr(i) for i in range(ord('ก'), ord('ฮ') + 1)])

ALLOWED_CHARS = set("abcdefghijklmnopqrstuvwxyzáéíóúúůřěščžABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -.,")

def parse_syllables(word):
    syllables = []
    i = 0
    length = len(word)

    while i < length:
        syllable = ""

        # 1. Leading vowel
        if word[i] in LEADING_VOWELS:
            syllable += word[i]
            i += 1

        # 2. Initial consonants (up to 2 for clusters)
        consonants_found = 0
        while i < length and word[i] in CONSONANTS:
            syllable += word[i]
            consonants_found += 1
            i += 1
            if consonants_found >= 2:
                # Basic heuristic for clusters
                if i < length and word[i] in CONSONANTS:
                    break

        # 3. Vowels above/below/following and tone marks
        while i < length and (word[i] in FOLLOWING_VOWELS or word[i] in TONE_MARKS or word[i] == SILENT_MARK or word[i] in ['อ', 'ย', 'ว']):
            if word[i] in ['อ', 'ย', 'ว'] and i+1 < length and (word[i+1] in FOLLOWING_VOWELS or word[i+1] in LEADING_VOWELS):
                break
            syllable += word[i]
            i += 1

        # 4. Final consonant
        if i < length and word[i] in CONSONANTS:
            # If the next character is a consonant or the end of string, this is a final.
            if i + 1 == length or word[i+1] in CONSONANTS or word[i+1] in LEADING_VOWELS:
                syllable += word[i]
                i += 1

        # If it didn't match any of the above (e.g. punctuation, numbers, unknown chars)
        if not syllable and i < length:
            syllable += word[i]
            i += 1

        syllables.append(syllable)

    return syllables

def transcribe(thai_word, rules):
    thai_word = thai_word.strip()
    
    lookup = load_lookup()
    if thai_word in lookup:
        return lookup[thai_word]

    if "exceptions" in rules and thai_word in rules["exceptions"]:
        return rules["exceptions"][thai_word]
        
    initials = rules.get("initials", {})
    finals = rules.get("finals", {})
    vowels = rules.get("vowels", {})
    compound_vowels = rules.get("compound_vowels", {})
    
    logger.info(f"Uncertain pattern applied for: {thai_word}")
    
    words = thai_word.split()
    res = []
    
    for w in words:
        syllables = parse_syllables(w)
        out_word = ""
        
        for syllable in syllables:
            clean_syl = syllable
            while SILENT_MARK in clean_syl:
                idx = clean_syl.find(SILENT_MARK)
                if idx > 0:
                    clean_syl = clean_syl[:idx-1] + clean_syl[idx+1:]
                else:
                    clean_syl = clean_syl[1:]
                    
            for tone in TONE_MARKS:
                clean_syl = clean_syl.replace(tone, '')
                
            cons = [c for c in clean_syl if c in CONSONANTS and c != 'อ']
            
            if not cons:
                for c in clean_syl:
                    if c in vowels:
                        out_word += vowels[c]
                    elif c in ALLOWED_CHARS:
                        out_word += c
                    else:
                        out_word += "?"
                        _log_unknown(c)
                continue

            initial_char = cons[0]
            if initial_char == 'ห' and len(cons) > 1:
                initial_char = cons[1]

            final_char = None
            if len(cons) > 1 and cons[-1] != initial_char:
                last_c_idx = clean_syl.rfind(cons[-1])
                if last_c_idx == len(clean_syl) - 1:
                    final_char = cons[-1]

            v_str = clean_syl.replace(initial_char, '', 1)
            if final_char:
                v_str = v_str[::-1].replace(final_char, '', 1)[::-1]

            if not v_str and final_char:
                v_snd = "o"
            elif not v_str and not final_char:
                v_snd = "a"
            else:
                for v_match, v_rep in sorted(compound_vowels.items(), key=lambda x: len(x[0]), reverse=True):
                    if v_match in v_str:
                        v_str = v_str.replace(v_match, v_rep)

                v_snd = ""
                cv_reps = set(compound_vowels.values())
                for c in v_str:
                    if c in vowels:
                        v_snd += vowels[c]
                    elif c in initials:
                        v_snd += initials[c]
                    elif c in cv_reps:
                        pass
                    elif c in ALLOWED_CHARS:
                        v_snd += c
                    else:
                        v_snd += "?"
                        _log_unknown(c)

            if initial_char in initials:
                out_word += initials[initial_char]
            else:
                out_word += "?"
                _log_unknown(initial_char)

            out_word += v_snd.replace('อ', 'ó').replace('ว', 'u').replace('ย', 'j').replace('ร', 'ó').replace('óó', 'ó').replace('aa', 'a')
            
            if final_char:
                if final_char in finals:
                    out_word += finals[final_char]
                elif final_char in initials:
                    out_word += initials[final_char]
                else:
                    out_word += "?"
                    _log_unknown(final_char)

        res.append(out_word)
        
    return " ".join(res)
