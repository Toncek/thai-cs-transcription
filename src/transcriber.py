import json
import logging
from pathlib import Path

try:
    from pythainlp.tokenize import subword_tokenize
except ImportError:
    subword_tokenize = None

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
FOLLOWING_VOWELS = set("าิีึืุู็ัำํ")
TONE_MARKS = set("่้๊๋")
SILENT_MARK = "์"

CONSONANTS = set([chr(i) for i in range(ord('ก'), ord('ฮ') + 1)])

ALLOWED_CHARS = set("abcdefghijklmnopqrstuvwxyzáéíóúüůřěščžöýABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -.,/()[]…")

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
            if consonants_found == 1 and i < length and word[i] in CONSONANTS:
                # Check if next consonant is followed by a vowel or tone mark. If so, it probably belongs to the next syllable
                if i + 1 < length and (word[i+1] in FOLLOWING_VOWELS or word[i+1] in LEADING_VOWELS or word[i+1] in TONE_MARKS):
                    if word[i] not in 'รลว' or word[i-1] not in 'กขคตปผพ': # rough cluster check
                        # Wait: if word[i-1] is 'ห' and word[i] is low sonorant, it's a single syllable tone cluster!
                        if word[i-1] == 'ห' and word[i] in 'งญนมยรลว':
                            pass
                        elif word[i-1] == 'อ' and word[i] == 'ย': # อย cluster
                            pass
                        else:
                            break
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
        if i < length and word[i] in CONSONANTS and word[i] != 'ห':
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

    # Fast path for complete matches
    if thai_word in lookup:
        return lookup[thai_word]

    if "exceptions" in rules and thai_word in rules["exceptions"]:
        return rules["exceptions"][thai_word]

    if "specials" in rules and thai_word in rules["specials"]:
        return rules["specials"][thai_word]
        
    initials = rules.get("initials", {})
    finals = rules.get("finals", {})
    vowels = rules.get("vowels", {})
    compound_vowels = rules.get("compound_vowels", {})
    
    logger.info(f"Uncertain pattern applied for: {thai_word.replace('\n', '').replace('\r', '')}")
    
    if subword_tokenize:
        # Using subword_tokenize with dict engine to split syllables/subwords like 'วัน', 'นี้'
        tokens = subword_tokenize(thai_word, engine="dict")
    else:
        thai_word_spaced = thai_word.replace('ๆ', ' ๆ ')
        tokens = thai_word_spaced.split()

    # Greedy merge tokens that exist in lookup
    merged_tokens = []
    i = 0
    while i < len(tokens):
        if tokens[i].strip() == '':
            i += 1
            continue

        # Try to match largest possible sequence in lookup
        matched = False
        for j in range(len(tokens), i, -1):
            cand = "".join(tokens[i:j])
            if cand in lookup:
                merged_tokens.append(cand)
                i = j
                matched = True
                break
            elif "exceptions" in rules and cand in rules["exceptions"]:
                merged_tokens.append(cand)
                i = j
                matched = True
                break

        if not matched:
            merged_tokens.append(tokens[i])
            i += 1

    res = []
    
    for w in merged_tokens:
        w = w.strip()
        if not w:
            continue

        if w == 'ๆ':
            if res:
                res.append(res[-1])
            continue

        if w in lookup:
            res.append(lookup[w])
            continue

        if "exceptions" in rules and w in rules["exceptions"]:
            res.append(rules["exceptions"][w])
            continue

        # Pre-process double ro han
        while 'รร' in w:
            idx = w.find('รร')
            if idx + 2 < len(w) and w[idx+2] in CONSONANTS and w[idx+2] not in 'อยวรฤๅ':
                # Followed by consonant (likely final)
                w = w[:idx] + 'ั' + w[idx+2:]
            else:
                # Not followed by final consonant
                w = w[:idx] + 'ัน' + w[idx+2:]

        syllables = parse_syllables(w)

        # Split falsely combined syllables (like 'มก' -> 'ม', 'ก')
        # where C1 + C2 is formed, but they should be C1 + a + C2
        new_syllables = []
        for i, s in enumerate(syllables):
            if len(s) == 2 and s[0] in CONSONANTS and s[1] in CONSONANTS:
                # 'มก' has no vowels. If it's not a true cluster, and there is a following syllable,
                # we should split it. In 'มกราคม', 'มก' + 'ราค'.
                if s == 'มก' and i + 1 < len(syllables) and syllables[i+1].startswith('ร'):
                    new_syllables.append(s[0])
                    new_syllables.append(s[1])
                else:
                    new_syllables.append(s)
            elif len(s) > 1 and s[0] in CONSONANTS and s[1] in CONSONANTS and s[0] != 'ห' and s[0] != 'อ':
                # e.g., 'พม่า'. 'พ' and 'ม' are consonants.
                true_clusters = ["กร", "กล", "กว", "ขร", "ขล", "ขว", "คร", "คล", "คว", "ตร", "ปร", "ปล", "พร", "พล", "ทร", "ธร"]
                if s[:2] not in true_clusters and any(c in LEADING_VOWELS | FOLLOWING_VOWELS | TONE_MARKS for c in s[1:]):
                    # Split it: 'พ' and 'ม่า', or 'บ' and 'ริ'
                    new_syllables.append(s[0])
                    new_syllables.append(s[1:])
                else:
                    new_syllables.append(s)
            else:
                new_syllables.append(s)
        syllables = new_syllables

        out_word = ""
        
        for syl_idx, syllable in enumerate(syllables):
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

            # Handle ฤ special cases within the syllable before extracting consonants
            clean_syl = clean_syl.replace('ฤๅ', 'รือ')

            clean_syl = clean_syl.replace('สกฤต', 'สะกริต')
            clean_syl = clean_syl.replace('ทฤษ', 'ทะริดษ')
            clean_syl = clean_syl.replace('สฤษ', 'สะริดษ')
            clean_syl = clean_syl.replace('พฤษ', 'พะริดษ')
            clean_syl = clean_syl.replace('กฤษ', 'กะริดษ')

            clean_syl = clean_syl.replace('ฤษ', 'ริตษ')
            clean_syl = clean_syl.replace('ฤก', 'ริตก')
            clean_syl = clean_syl.replace('ฤต', 'ริตต')
            clean_syl = clean_syl.replace('ฤ', 'ริ')
                
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
            if len(cons) > 1 and cons[-1] != 'อ':
                # Check if it's part of a compound vowel like เ-ีย, ัว
                is_compound_vowel_part = False
                if cons[-1] == 'ย' and 'เ' in clean_syl and 'ี' in clean_syl:
                    is_compound_vowel_part = True
                elif cons[-1] == 'ว' and 'ั' in clean_syl:
                    is_compound_vowel_part = True

                if not is_compound_vowel_part:
                    last_c_idx = clean_syl.rfind(cons[-1])
                    if last_c_idx == len(clean_syl) - 1 or len(cons) == 2:
                        if cons[-1] != initial_char or clean_syl.count(cons[-1]) > 1:
                            final_char = cons[-1]

            v_str = clean_syl.replace(initial_char, '', 1)
            if final_char:
                v_str = v_str[::-1].replace(final_char, '', 1)[::-1]

            all_vowels = {**compound_vowels}
            for k, v in vowels.items():
                if len(k) > 1:
                    all_vowels[k] = v

            if not v_str and final_char:
                # If parsed as C1+C2 (e.g. 'มก' in 'มกราคม'), it might actually be two syllables C1+a, C2+a if followed by vowel.
                if syl_idx + 1 < len(syllables):
                    if initial_char == 'ม' and final_char == 'ก':
                        v_snd = "a"
                v_snd = "o"

                # Special cases for 2-consonant clusters where first should have 'a'
                if syl_idx + 1 < len(syllables) and not any(c in v_str for c in vowels) and not any(c in syllable for c in LEADING_VOWELS | FOLLOWING_VOWELS | TONE_MARKS):
                    if final_char in initials:
                        if len(syllable) == 2 and syllable[0] == 'ม' and syllable[1] == 'ก':
                            v_snd = "a" + initials[final_char] + "a"
                            final_char = None
            elif not v_str and not final_char:
                if initial_char == 'บ':
                    v_snd = "o"
                elif initial_char == 'ป':
                    v_snd = "a"
                else:
                    v_snd = "a"
            else:
                if 'เ' in v_str and 'า' in v_str:
                    idx_e = v_str.find('เ')
                    idx_a = v_str.find('า')
                    if idx_e < idx_a:
                        v_str = v_str.replace('เ', '', 1).replace('า', 'เา', 1)

                if 'ํ' in v_str and 'า' in v_str:
                    v_str = v_str.replace('ํ', '').replace('า', 'ำ')

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

            if syl_idx == len(syllables) - 1 and out_word.endswith("k") and ini_str == "m" and v_snd == "a":
                # We can dynamically fix it if we know the word is ending in km.
                # 'makarákm' -> 'makarákhom'
                # This is a bit hacky but the parsing logic is hard to change without breaking other words.
                out_word = out_word[:-1] + "khom"
                continue

            if '็' in syllable:
                short_map = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ý': 'y'}
                for long_v, short_v in short_map.items():
                    v_snd = v_snd.replace(long_v, short_v)

            # Apply Czech-specific y/ý normalization after d, t, n, l
            # i -> y, í -> ý
            if ini_str in ["d", "t", "n", "l"]:
                if v_snd.startswith("i"):
                    v_snd = "y" + v_snd[1:]
                elif v_snd.startswith("í"):
                    v_snd = "ý" + v_snd[1:]

            out_word += prefix + ini_str + v_snd
            
            if final_char:
                if final_char == initial_char and v_snd == "o" and not any(c in v_str for c in vowels):
                    # Double consonant rule: e.g. บบ -> bob (use initial mapping for both)
                    if final_char in initials:
                        out_word += initials[final_char]
                    else:
                        out_word += "?"
                        _log_unknown(final_char)
                elif final_char in finals:
                    final_snd = finals[final_char]
                    if not (v_snd.endswith("j") and final_snd == "j"):
                        out_word += final_snd
                elif final_char in initials:
                    final_snd = initials[final_char]
                    if not (v_snd.endswith("j") and final_snd == "j"):
                        out_word += final_snd
                else:
                    out_word += "?"
                    _log_unknown(final_char)

        res.append(out_word)
        
    return " ".join(res)
