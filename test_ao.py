from src.transcriber import transcribe, load_rules
rules = load_rules()
print(transcribe('เก่า', rules))
print(transcribe('เอา', rules))
print(transcribe('เตา', rules))
