import src.transcriber as t
thai = 'นํ้า'
rules = t.load_rules()
print(t.transcribe(thai, rules))
