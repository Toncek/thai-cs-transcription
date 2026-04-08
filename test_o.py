from src.transcriber import transcribe, load_rules
rules = load_rules()
print(transcribe('อะไร', rules))
print(transcribe('อยาก', rules))
print(transcribe('อยู่', rules))
print(transcribe('อยาง', rules))
