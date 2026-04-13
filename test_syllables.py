import src.transcriber as t
rules = t.load_rules()
print(t.transcribe('แม่', rules))
print(t.transcribe('นํ้า', rules))
print(t.transcribe('แม่นํ้า', rules))
