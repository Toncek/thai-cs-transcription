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

ALLOWED_CHARS = set("abcdefghijklmnopqrstuvwxyzáéíóúúůřěščžöABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -.,")

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
    
    logger.info(f"Uncertain pattern applied for: {thai_word.replace('\n', '').replace('\r', '')}")
    
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

            # Remove mai taikhu (็) which acts as a vowel shortener,
            # its effect is usually implicitly handled by rules/lookup,
            # we just prevent it from emitting '?'
            clean_syl = clean_syl.replace('็', '')
                
            cons = [c for c in clean_syl if c in CONSONANTS]
            
            if 'อ' in cons and len(cons) > 1:
                pass

            if not cons:
                # Need to handle เ-า / เอา when there are no consonants (e.g., 'เอา' starts with 'อ' which gets removed from cons but is an initial)
                # But wait, 'อ' is an initial. Why is 'อ' removed from cons?
                # `cons = [c for c in clean_syl if c in CONSONANTS and c != 'อ']` removes 'อ'.
                # But 'อ' IS a consonant! Let's not fully remove it if it's the ONLY consonant,
                # or we just process it.
                v_str = clean_syl

                # Check for เา combination in v_str
                if 'เ' in v_str and 'า' in v_str:
                    v_str = v_str.replace('เ', '', 1).replace('า', 'เา', 1)

                all_vowels = {**compound_vowels}
                for k, v in vowels.items():
                    if len(k) > 1:
                        all_vowels[k] = v

                for v_match, v_rep in sorted(all_vowels.items(), key=lambda x: len(x[0]), reverse=True):
                    if v_match in v_str:
                        v_str = v_str.replace(v_match, v_rep)

                for c in v_str:
                    if c in vowels:
                        out_word += vowels[c]
                    elif c in ALLOWED_CHARS:
                        out_word += c
                    else:
                        out_word += "?"
                        _log_unknown(c)

                # If the syllable is just 'อ' (ó) and then vowels, and it's acting as a silent consonant,
                # we don't need 'ó' before 'ao' or 'a' etc.
                # However, for now, let's keep the existing logic and fix 'อ' specifically.
                out_word = out_word.replace('อ', 'ó').replace('ว', 'u').replace('ย', 'j').replace('ร', 'ó').replace('óó', 'ó').replace('aa', 'a')

                # If output starts with ó and is followed by a vowel, drop the ó (silent อ)
                if len(out_word) > 1 and out_word.startswith('ó') and out_word[1] in 'aáeéiíoóuúýy':
                    out_word = out_word[1:]

                continue

            initial_char = cons[0]

            # Remove leading silent tone-carrier ห before low sonorants (ง, ญ, น, ม, ย, ร, ล, ว)
            # If ห is followed by one of these, we should ignore it as an initial consonant
            # However, in current logic, `cons` might contain more than just initials.
            # If `initial_char == 'ห'` and the next consonant is a low sonorant, we replace it.
            # IMPORTANT: We must ensure that cons[1] is actually adjacent or part of the cluster.
            # If the syllable is `เห็น` (hén), cons = ['ห', 'น']. But `น` is the final consonant!
            # We shouldn't remove `ห` if `น` is a final consonant.
            # Usually, if `cons` has 2 elements and the second is the final, `ห` is the ONLY initial.
            # So, only remove `ห` if it's immediately before the low sonorant orthographically
            # (or at least, they are both part of the initial cluster).
            if initial_char == 'ห' and len(cons) > 1 and cons[1] in 'งญนมยรลว':
                is_final = False

                idx_h_orig = syllable.find('ห')
                idx_c1_orig = syllable.find(cons[1])
                between_orig = syllable[idx_h_orig+1:idx_c1_orig]
                if any(c in FOLLOWING_VOWELS or c in TONE_MARKS for c in between_orig):
                    is_final = True

                has_any_vowel = any(c in LEADING_VOWELS or c in FOLLOWING_VOWELS for c in clean_syl)
                if not has_any_vowel and len(cons) == 2:
                    is_final = True

                idx_c1 = clean_syl.find(cons[1])
                if idx_c1 == len(clean_syl) - 1:
                    if 'เ' in clean_syl and not any(c in FOLLOWING_VOWELS for c in clean_syl) and '็' not in syllable:
                        is_final = True

                if not is_final:
                    initial_char = cons[1]
                    clean_syl = clean_syl.replace('ห', '', 1)

            prefix = ""
            if 'อ' in clean_syl and clean_syl.find('อ') == 0 and len(cons) > 1 and cons[1] == 'ย':
                initial_char = 'ย'
                clean_syl = clean_syl.replace('อ', '', 1)
            elif 'อ' in clean_syl and clean_syl.find('อ') == 0 and initial_char == 'อ' and len(cons) > 1:
                idx_h = clean_syl.find('อ')
                idx_c1 = clean_syl.find(cons[1])
                is_o_final = False
                if idx_c1 == len(clean_syl) - 1:
                    between = clean_syl[idx_h+1:idx_c1]
                    if any(c in FOLLOWING_VOWELS or c in LEADING_VOWELS or c in vowels for c in between) or 'า' in clean_syl:
                        is_o_final = True

                if not is_o_final:
                    initial_char = cons[1]
                    prefix = "a"
                    clean_syl = clean_syl.replace('อ', '', 1)

            final_char = None
            if len(cons) > 1 and cons[-1] != initial_char and cons[-1] != 'อ':
                last_c_idx = clean_syl.rfind(cons[-1])
                if last_c_idx == len(clean_syl) - 1 or len(cons) == 2:
                    final_char = cons[-1]

            v_str = clean_syl.replace(initial_char, '', 1)
            if final_char:
                v_str = v_str[::-1].replace(final_char, '', 1)[::-1]

            all_vowels = {**compound_vowels}
            for k, v in vowels.items():
                if len(k) > 1:
                    all_vowels[k] = v

            if not v_str and final_char:
                v_snd = "o"
            elif not v_str and not final_char:
                v_snd = "a"
            else:
                if 'เ' in v_str and 'า' in v_str:
                    idx_e = v_str.find('เ')
                    idx_a = v_str.find('า')
                    if idx_e < idx_a:
                        v_str = v_str.replace('เ', '', 1).replace('า', 'เา', 1)

                for v_match, v_rep in sorted(all_vowels.items(), key=lambda x: len(x[0]), reverse=True):
                    if v_match in v_str:
                        v_str = v_str.replace(v_match, v_rep)

                v_snd = ""
                for c in v_str:
                    if c in vowels:
                        v_snd += vowels[c]
                    elif c in ALLOWED_CHARS:
                        v_snd += c
                    elif c in initials:
                        v_snd += initials[c]
                    else:
                        v_snd += "?"
                        _log_unknown(c)

            ini_str = ""
            if initial_char in initials:
                ini_str = initials[initial_char]
            else:
                ini_str = "?"
                _log_unknown(initial_char)

            v_snd = v_snd.replace('อ', 'ó').replace('ว', 'u').replace('ย', 'j').replace('ร', 'ó').replace('óó', 'ó').replace('aa', 'a')

            if v_snd.startswith('ó'):
                if len(v_snd) > 1 and v_snd[1] in 'aáeéiíoóuúýy':
                    v_snd = v_snd[1:]

            if initial_char == 'อ' and v_snd.startswith('ó'):
                if len(v_snd) > 1:
                    v_snd = v_snd[1:]



            # Apply Czech-specific y/ý normalization after d, t, n, l
            # i -> y, í -> ý
            if ini_str in ["d", "t", "n", "l"]:
                if v_snd.startswith("i"):
                    v_snd = "y" + v_snd[1:]
                elif v_snd.startswith("í"):
                    v_snd = "ý" + v_snd[1:]

            out_word += prefix + ini_str + v_snd
            
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
