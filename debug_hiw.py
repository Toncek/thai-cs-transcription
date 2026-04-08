from src.transcriber import transcribe, load_rules
rules = load_rules()
print(transcribe('หิว', rules))
