from src.transcriber import transcribe, load_rules
import logging
logging.basicConfig(level=logging.DEBUG)
rules = load_rules()
print(transcribe('เห็น', rules))
print(transcribe('ใหม่', rules))
