import src.transcriber as t
rules = t.load_rules()
thai = 'แม่นํ้า'
print("parse", t.parse_syllables(thai))
for w in thai.split():
    syllables = t.parse_syllables(w)
    for s in syllables:
        print("syl", s)
