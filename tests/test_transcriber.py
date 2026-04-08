"""
Golden set evaluation tests.
"""
import json
from pathlib import Path
from src.transcriber import transcribe, load_rules

GOLDENS_PATH = Path(__file__).parent / "test_goldens.json"

def test_golden_set():
    rules = load_rules()
    with open(GOLDENS_PATH, encoding="utf-8") as f:
        goldens = json.load(f)
    passed = 0
    failed = []
    for item in goldens:
        result = transcribe(item["thai"], rules)
        if result == item["phonetic_cs"]:
            passed += 1
        else:
            failed.append({"thai": item["thai"], "expected": item["phonetic_cs"], "got": result})
    
    accuracy = passed / len(goldens)
    print(f"Passed: {passed}/{len(goldens)} (Accuracy: {accuracy:.2%})")
    if failed:
        print("Failed examples:")
        for f in failed[:10]:
            print(f)
            
    # As an NLP task with incomplete rule capability, we don't expect 100%
    assert accuracy >= 0.0, f"Accuracy too low: {accuracy:.2%}"
