import json
from pathlib import Path
from src.transcriber import transcribe, load_rules
import src.transcriber as t

def test_regression_cases():
    rules = load_rules()
    t._LOOKUP_CACHE = {}  # force rule engine

    bad_cases_path = Path(__file__).parent / "regression_bad_cases.json"
    with open(bad_cases_path, "r", encoding="utf-8") as f:
        cases = json.load(f)

    expected_outputs = {
        "เล็ก": "lek",
        "เป็น": "pen",
        "เห็น": "hen",
        "หิว": "hiu",
        "ใหญ่": "jaj",
        "ใหม่": "maj",
        "อะไร": "araj",
        "เก่า": "kao",
        "เอา": "ao",
        "เงิน": "gön",
        "อร่อย": "arój",
        "อย่างไร": "jángraj",
        "อ่าน": "án",
        "ที่นั่น": "týnan",
        "ระบบ": "rabob",
        "เสีย": "sia",
        "ไทย": "taj",
        "คือ": "khü",
        "ทำให้": "tamhaj",
        "กฎหมาย": "kotmáj",
        "ทำงาน": "tamgán"
    }

    for case in cases:
        thai = case["thai"]
        out = transcribe(thai, rules)
        assert out == expected_outputs[thai], f"Regression failed for {thai}: got {out}, expected {expected_outputs[thai]}"
