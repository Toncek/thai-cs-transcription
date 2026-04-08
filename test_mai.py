from src.transcriber import transcribe, load_rules
rules = load_rules()
print(transcribe('เล็ก', rules))
print(transcribe('เป็น', rules))
