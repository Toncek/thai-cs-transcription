import src.transcriber as t
rules = t.load_rules()
print(repr(t.transcribe('แม่ นํ้า', rules)))
