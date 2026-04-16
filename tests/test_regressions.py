import json
from pathlib import Path
from src.transcriber import transcribe, load_rules
import src.transcriber

def test_regression_cases():
    rules = load_rules()
    src.transcriber._LOOKUP_CACHE = {}  # force rule engine

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
        "อะไร": "a raj",
        "เก่า": "kao",
        "เอา": "ao",
        "เงิน": "gön",
        "อร่อย": "arój",
        "อย่างไร": "jáng raj",
        "อ่าน": "án",
            "ที่นั่น": "thí nan",
        "ระบบ": "ra bob",
        "เสีย": "sia",
            "ไทย": "thaj",
        "คือ": "khü",
            "ทำให้": "tham haj",
        "กฎหมาย": "kot máj",
            "ทำงาน": "tham gán"
    }

    for case in cases:
        thai = case["thai"]
        out = transcribe(thai, rules)
        assert out == expected_outputs[thai], f"Regression failed for {thai}: got {out}, expected {expected_outputs[thai]}"

def test_multiword_transcription():
    rules = load_rules()
    src.transcriber._LOOKUP_CACHE = {}  # force rule engine

    cases = {
        "วันนี้": "van ný",
        "วันนี้วันจันทร์": "van ný van džantha",
        "เจอกันตอนบ่าย": "džéó kan tón báj",
        "สวัสดีครับ": "savat dý khrap",
        "สามชั่วโมง": "sám čúa móng"
    }

    for thai, expected in cases.items():
        out = transcribe(thai, rules)
        assert " " in out, f"Multiword failed, expected space in {thai}: got {out}"
        assert out == expected, f"Expected {expected}, got {out}"

def test_special_chars():
    rules = load_rules()
    src.transcriber._LOOKUP_CACHE = {}

    # Tests that parentheses, brackets, and Latin letters passthrough without ?
    out = transcribe("A(ทดสอบ)[x]/…", rules)
    assert "?" not in out, f"Expected no '?' in output, got: {out}"
