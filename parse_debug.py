import src.transcriber as t
thai = 'ทะเลดํา'
syls = []
i = 0
while i < len(thai):
    syl = ""
    if thai[i] in t.LEADING_VOWELS:
        syl += thai[i]; i+=1

    c_found = 0
    while i < len(thai) and thai[i] in t.CONSONANTS:
        syl += thai[i]; c_found += 1; i+=1
        if c_found == 1 and i < len(thai) and thai[i] in t.CONSONANTS:
            # Check if next consonant is followed by vowel
            if i+1 < len(thai) and (thai[i+1] in t.FOLLOWING_VOWELS or thai[i+1] in t.LEADING_VOWELS):
                break
        if c_found >= 2:
            if i < len(thai) and thai[i] in t.CONSONANTS:
                break

    while i < len(thai) and (thai[i] in t.FOLLOWING_VOWELS or thai[i] in t.TONE_MARKS or thai[i] == t.SILENT_MARK or thai[i] in ['อ', 'ย', 'ว']):
        syl += thai[i]; i+=1

    if i < len(thai) and thai[i] in t.CONSONANTS and thai[i] != 'ห':
        if i + 1 == len(thai) or thai[i+1] in t.CONSONANTS or thai[i+1] in t.LEADING_VOWELS:
            syl += thai[i]; i+=1
    if not syl and i < len(thai):
        syl += thai[i]; i+=1
    syls.append(syl)
print(syls)
