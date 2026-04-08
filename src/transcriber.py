import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def load_rules(rules_path=None):
    if rules_path is None:
        rules_path = Path(__file__).parent.parent / "spec" / "rules.json"
    with open(rules_path, "r", encoding="utf-8") as f:
        return json.load(f)

def transcribe(thai_word, rules):
    thai_word = thai_word.strip()
    
    if "exceptions" in rules and thai_word in rules["exceptions"]:
        return rules["exceptions"][thai_word]
        
    initials = rules.get("initials", {})
    finals = rules.get("finals", {})
    vowels = rules.get("vowels", {})
    compound_vowels = rules.get("compound_vowels", {})
    
    logger.info(f"Uncertain pattern applied for: {thai_word}")
    
    # Sort compound vowels by length to match the longest first
    sorted_compounds = sorted(compound_vowels.items(), key=lambda x: len(x[0]), reverse=True)
    
    words = thai_word.split()
    res = []
    
    for w in words:
        # Remove silent letters using the rule
        while '์' in w:
            idx = w.find('์')
            if idx > 0:
                w = w[:idx-1] + w[idx+1:]
            else:
                w = w[1:]
                
        # Tone marks
        for tone in ['่', '้', '๊', '๋']:
            w = w.replace(tone, '')
            
        consonants = [c for c in w if c in initials and c != 'อ']
        
        if not consonants:
            out = ""
            for c in w:
                out += vowels.get(c, c)
            res.append(out)
            continue
            
        initial_idx = w.find(consonants[0])
        initial_char = w[initial_idx]
        
        if initial_char == 'ห' and len(consonants) > 1:
            initial_idx = w.find(consonants[1])
            initial_char = w[initial_idx]
            w = w.replace('ห', '', 1)
            
        final_idx = -1
        if len(consonants) > 1:
            for i in range(len(w)-1, initial_idx, -1):
                if w[i] in finals:
                    final_idx = i
                    break
                    
        v_str = w.replace(initial_char, '', 1)
        if final_idx != -1:
            final_char = w[final_idx]
            v_str = v_str[::-1].replace(final_char, '', 1)[::-1]
            
        for v_match, v_rep in sorted_compounds:
            if v_match in v_str:
                v_str = v_str.replace(v_match, v_rep)
                
        v_snd = ""
        for c in v_str:
            v_snd += vowels.get(c, c)
            
        v_snd = v_snd.replace('อ', 'ó').replace('ว', 'u').replace('ย', 'j').replace('ร', 'ó')
        v_snd = v_snd.replace('óó', 'ó').replace('aa', 'a')
        
        out = ""
        out += initials.get(initial_char, "")
        out += v_snd
        
        if not v_snd and final_idx != -1:
            out += "o"
        elif not v_snd and final_idx == -1:
            out += "a"
            
        if final_idx != -1:
            final_char = w[final_idx]
            out += finals.get(final_char, initials.get(final_char, ""))
            
        res.append(out)
        
    return " ".join(res)
