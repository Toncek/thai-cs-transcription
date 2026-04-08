from src.transcriber import transcribe, load_rules
rules = load_rules()
print(transcribe('ดี', rules))
print(transcribe('ที่', rules))
print(transcribe('นี้', rules))
print(transcribe('ลิขสิทธิ์', rules))
