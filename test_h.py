from src.transcriber import transcribe, load_rules
rules = load_rules()
print(transcribe('หิว', rules))
print(transcribe('ใหม่', rules))
print(transcribe('ใหญ่', rules))
print(transcribe('หวัง', rules))
