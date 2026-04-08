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
                
            cons = [c for c in clean_syl if c in CONSONANTS and c != 'อ']
            
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
                # Check if 'ห' and cons[1] are adjacent or only separated by vowels/tones, and not separated by the vowel that normally wraps them
                # Actually, an easier check is to see if `ห` and `cons[1]` are both before the main vowel.
                # But since Thai vowels can be before, after, above, below...
                # If they are both initials, they usually appear together. If cons[1] is a final, it's at the end.
                # In 'เห็น', 'ห' is at index 1, 'น' is at index 3. 'เ' is at 0, '็' is at 2.
                # In 'ใหม่', 'ห' is at index 1, 'ม' is at index 2.
                # In 'ใหญ่', 'ห' is at index 1, 'ญ' is at index 2.
                idx_h = clean_syl.find('ห')
                idx_sonorant = clean_syl.find(cons[1])
                if idx_sonorant > idx_h and idx_sonorant - idx_h <= 2:
                    # They are close enough to be an initial cluster.
                    # If it's 'เห็น', clean_syl is 'เหน'. 'ห' is 1, 'น' is 2. Wait! 'เห็น' without '็' is 'เหน'. idx_h=1, idx_n=2.
                    # Wait, if clean_syl is 'เหน' then cons[1] is 'น'.
                    # Is 'น' a final?
                    # Let's check `parse_syllables`. It groups leading vowel 'เ', initials 'ห', then it should take '็', then 'น'.
                    # Let's just explicitly check if cons[1] is the final_char later, but we haven't computed final_char yet.
                    pass

                # A safer heuristic: is there a third consonant?
                # If len(cons) == 2, and cons[1] is the last character, then cons[1] is likely final.
                # In 'หิว', cons=['ห', 'ว']. 'ว' is a low sonorant but it is the final consonant.
                # However, is 'หิว' pronounced with 'h'? Yes, "hiu".
                # But wait, หิว means hungry. Pronunciation is hǐw. It is NOT silent h!
                # Wait, 'ว' is a low sonorant, but 'ห' here is a leading consonant, and 'ว' is a final!
                # So the heuristic works: 'ว' is at the end.

                is_final = False
                # What if the consonant is a final? In parse_syllables, if it's the last character
                # and not followed by a vowel in the syllable.
                # Actually, check if the second consonant is after a vowel or tone mark.
                # If there's a vowel character between 'ห' and cons[1], it's probably a final.
                # In หิว (h i w), i (ิ) is between h and w.
                idx_h = clean_syl.find('ห')
                idx_c1 = clean_syl.find(cons[1])
                # If there are characters between 'ห' and cons[1] other than tone marks or 'อ', it's a final.
                # For now, let's just check if it's at the end of the syllable.
                if idx_c1 == len(clean_syl) - 1:
                    # In 'ใหม่', clean_syl='ใหม', len=3, 'ม' is at 2. So idx_c1 is 2, len-1 is 2.
                    # It thinks 'ม' is final!
                    # But 'ใ' is a LEADING_VOWEL. 'ม' is an initial. 'ใหม่' has no final!
                    # So if idx_c1 == len(clean_syl) - 1, it might still not be a final if there's no trailing vowel/final.
                    # Let's verify if `cons[1]` is a final based on `len(cons)` and position.
                    # A better way: if there are only 2 consonants and no other vowels after `cons[1]`, is it final?
                    # In หิว, i (ิ) is a following vowel BEFORE ว.
                    # Let's check if there is a vowel between them.
                    # Find any character in `vowels` or `FOLLOWING_VOWELS` between `ห` and `cons[1]`
                    between = clean_syl[idx_h+1:idx_c1]
                    if any(c in FOLLOWING_VOWELS or c in LEADING_VOWELS or c in vowels for c in between):
                        is_final = True
                    # Also, if `cons[1]` is followed by nothing, but there's a leading vowel, it could be an initial cluster.
                    # If `cons[1]` is followed by nothing and there's no vowel anywhere, it's 'หก' (hok) - final.
                    # Wait, in 'ใหม่', `clean_syl` is `ใหม`. 'ใ' is leading. `between` is empty ('ห' is 1, 'ม' is 2).
                    # So `is_final` will be False.
                    # In 'เห็น', `clean_syl` is `เหน`. `between` is empty ('ห' is 1, 'น' is 2).
                    # Wait, in 'เห็น', there is 'เ' at 0. 'ห' is 1, 'น' is 2. `between` is empty. So 'น' will not be marked as final!
                    pass

                # Let's rethink. `parse_syllables` groups: LEADING_VOWEL, INITIALS, FOLLOWING_VOWELS, FINAL.
                # Since we just parsed it, we can just use the fact that if len(cons) == 2,
                # cons[1] is the final ONLY if the first one is the ONLY initial.
                # Does `ห` form a valid initial cluster with `งญนมยรลว`? Yes!
                # Is it ever NOT a cluster?
                # If `ห` is followed by a sonorant, it's ALMOST ALWAYS a tone-carrier initial cluster,
                # EXCEPT when `ห` is the ONLY initial and the sonorant is the FINAL (e.g. หิว 'hiu', หิน 'hin', หุบ 'hup' -> here 'บ' is not sonorant, but 'น', 'ว', 'ม' can be finals).
                # Example: หิน (hin) -> cons=['ห', 'น']. Is 'น' the final? Yes. Is 'ห' the initial? Yes.
                # How to distinguish 'หิน' from 'หนิ' (ni)?
                # In 'หิน', 'ิ' is at index 1. clean_syl='หิน' -> 'ห'(0) 'ิ'(1) 'น'(2). 'น' is after the vowel.
                # In 'หนิ', 'ิ' is at index 2. clean_syl='หนิ' -> 'ห'(0) 'น'(1) 'ิ'(2). 'น' is before the vowel.
                # So if the vowel is BEFORE `cons[1]`, `cons[1]` is final.

                # Check if there is any vowel before cons[1] and after ห in the original word.
                # Since `clean_syl` might have removed tones, we can check `clean_syl`.
                # If there's a FOLLOWING_VOWEL before `cons[1]`, then `cons[1]` is final.
                # What about LEADING_VOWELS? They are before `ห`, so they don't separate `ห` and `cons[1]`.
                # Let's check if there is a character from FOLLOWING_VOWELS between `ห` and `cons[1]`.

                is_final = False
                # What if `cons[1]` is the last character in the syllable AND there is a leading vowel, e.g., เห็น (hen)?
                # `clean_syl` = "เหน" (since ็ is removed). `cons` = ['ห', 'น'].
                # Here `ห` is the ONLY initial. `น` is the final.
                # In 'ใหม่', `clean_syl` = "ใหม". `cons` = ['ห', 'ม']. Here `ห` AND `ม` are initials. NO final.
                # How to distinguish?
                # In 'เห็น', it's เ-ะ mapped to e, meaning short vowel, short vowel needs final.
                # If the syllable has a leading vowel AND the consonant is the last char, is it a final?
                # Yes, in Thai, if a syllable is `เ + cons + cons`, the second is usually a final, UNLESS there's an implicit vowel.
                # But `เ` doesn't take implicit vowels after the second consonant.
                # Let's use the syllable parser's logic! The syllable parser ALREADY extracted `syllable`.
                # In 'ใหม่', `syllable` is 'ใหม่'. In 'เห็น', `syllable` is 'เห็น'.
                # If `cons[1]` is followed by nothing in `clean_syl`, could it be an initial?
                # In 'ใหม่', 'ม' is the last char. In 'เห็น', 'น' is the last char.
                # BUT 'เห็น' had '็' between 'ห' and 'น' in original word!
                # Ah! We stripped `็`.

                idx_h_orig = syllable.find('ห')
                idx_c1_orig = syllable.find(cons[1])
                between_orig = syllable[idx_h_orig+1:idx_c1_orig]
                if any(c in FOLLOWING_VOWELS or c in TONE_MARKS for c in between_orig):
                    is_final = True

                has_any_vowel = any(c in LEADING_VOWELS or c in FOLLOWING_VOWELS for c in clean_syl)
                if not has_any_vowel and len(cons) == 2:
                    is_final = True

                # Another case: เ + ห + cons. e.g. เหน. if `cons[1]` is final, 'เหน' has no other vowels.
                # If `clean_syl` is 'เหน', `between_orig` is empty (since there are no marks between ห and น).
                # Is 'น' final? Yes, "hen".
                # But what if 'เหม' in 'เหม็น' (hem)? We stripped ็.
                # In 'เหลว' (leo), 'ว' is final.
                # What if it's 'เหล' (le)? 'ล' is part of initial.
                # In 'เหมา' (mao), 'ม' is initial. 'า' is AFTER 'ม'. So `cons[1]` is not the last char.

                # Wait, what if the syllable ends with the consonant?
                idx_c1 = clean_syl.find(cons[1])
                if idx_c1 == len(clean_syl) - 1:
                    if 'เ' in clean_syl and not any(c in FOLLOWING_VOWELS for c in clean_syl) and '็' not in syllable:
                        # In this case (e.g. เหน or เหล), it's ambiguous. We default to it being a final,
                        # UNLESS it is mapped to an exception or in the lookup table (like เหม็น has ็).
                        # Let's say is_final = True by default for เ+ห+cons unless it's a known non-final.
                        is_final = True

                # Actually, wait. 'เห็น' hén HAS '็' in syllable!
                # So `any(c in ... or c in TONE_MARKS for c in between_orig)`
                # Wait! 'เห็น' means "see".
                # Pronunciation is hěn.
                # Initial is h. Vowel is e. Final is n.
                # Is it pronounced with h? YES.
                # Are the letters: ห(h), เ(e), ็(short), น(n).
                # Wait, "เห็น" does NOT have a silent ห modifying a low sonorant!!
                # It is just "h" + "e" + "n"!
                # The word is ห + เ + ็ + น. There is NO low sonorant initial. 'น' is the final.
                # So if 'น' is final, 'ห' is the ONLY initial. It's not a cluster!
                # The condition `initial_char == 'ห' and len(cons) > 1 and cons[1] in 'งญนมยรลว'` matches because 'น' is a low sonorant.
                # But 'น' is FINAL.
                # If `is_final` is True, we do NOT remove 'ห'.
                # So initial_char remains 'ห'.
                # BUT in my previous change, if `not is_final`, I set `initial_char = cons[1]` and removed `ห`.
                # Wait, if `is_final` is True for 'เห็น', then `not is_final` is False.
                # So it does NOT remove 'ห'.
                # So initial_char remains 'ห'.
                # Then why did it output `né`? Let's trace `né` for `เห็น`.

                if not is_final:
                    initial_char = cons[1]
                    # Also remove ห from clean_syl so it doesn't get processed as a vowel or extra
                    clean_syl = clean_syl.replace('ห', '', 1)

            # Handle silent 'อ' before 'ย' as an initial consonant cluster modifier
            # In words like อยาง, อยาก, อ is a silent tone modifier
            if 'อ' in clean_syl and clean_syl.find('อ') == 0 and len(cons) > 0 and cons[0] == 'ย':
                clean_syl = clean_syl.replace('อ', '', 1)

            final_char = None
            if len(cons) > 1 and cons[-1] != initial_char:
                last_c_idx = clean_syl.rfind(cons[-1])
                if last_c_idx == len(clean_syl) - 1:
                    final_char = cons[-1]

            v_str = clean_syl.replace(initial_char, '', 1)
            if final_char:
                v_str = v_str[::-1].replace(final_char, '', 1)[::-1]

            # Sort compound vowels and base vowels longer than 1 character first
            all_vowels = {**compound_vowels}
            for k, v in vowels.items():
                if len(k) > 1:
                    all_vowels[k] = v

            if not v_str and final_char:
                v_snd = "o"
            elif not v_str and not final_char:
                v_snd = "a"
            else:
                # Pre-process v_str to check for 'เ' + ... + 'า'
                if 'เ' in v_str and 'า' in v_str:
                    idx_e = v_str.find('เ')
                    idx_a = v_str.find('า')
                    if idx_e < idx_a:
                        # Convert to 'เา' explicitly if they wrap the consonant conceptually
                        # Actually they are already collected in v_str without the initial
                        v_str = v_str.replace('เ', '', 1).replace('า', 'เา', 1)

                for v_match, v_rep in sorted(all_vowels.items(), key=lambda x: len(x[0]), reverse=True):
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

            ini_str = ""
            if initial_char in initials:
                ini_str = initials[initial_char]
            else:
                ini_str = "?"
                _log_unknown(initial_char)

            # If the initial is อ, it's just a silent vowel carrier, but our dict maps it to "".
            # Sometimes 'ย' follows 'อ' forming a single initial 'ย' (e.g. อยาก -> 'j'ák).
            # We need to handle this explicitly if 'อ' is followed by 'ย'
            # Wait, 'อ' was excluded from `cons` entirely earlier.
            # Oh, if `cons` didn't have 'อ', `initial_char` is NOT 'อ', it would be 'ย'.
            # So `อยาก` initial_char is 'ย'. Wait, let's see why it's outputting 'jóú' for อยู่.
            # 'อยู่' -> cons=['ย']. v_str has 'อ', 'ู', '่'. tone marks are removed, so 'อ', 'ู'.
            # That's why 'อ' is in `v_str` and gets mapped to 'ó'!!

            v_snd = v_snd.replace('อ', 'ó').replace('ว', 'u').replace('ย', 'j').replace('ร', 'ó').replace('óó', 'ó').replace('aa', 'a')

            # If the output vowel sound starts with 'ó' (from 'อ' placeholder)
            # and is immediately followed by actual vowels, 'อ' is just a placeholder and should be removed.
            if len(v_snd) > 1 and v_snd.startswith('ó') and v_snd[1] in 'aáeéiíoóuúýy':
                v_snd = v_snd[1:]

            # Apply Czech-specific y/ý normalization after d, t, n, l
            # i -> y, í -> ý
            if ini_str in ["d", "t", "n", "l"]:
                if v_snd.startswith("i"):
                    v_snd = "y" + v_snd[1:]
                elif v_snd.startswith("í"):
                    v_snd = "ý" + v_snd[1:]

            out_word += ini_str + v_snd
            
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
