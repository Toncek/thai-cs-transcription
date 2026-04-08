from src.transcriber import transcribe, load_rules
rules = load_rules()
print(transcribe('เล็ก', rules))
print(transcribe('เป็น', rules))
print(transcribe('เด็ก', rules))
print(transcribe('เห็น', rules))
print(transcribe('เย็น', rules))
