"""
Thai → Czech phonetic transcriber.
Deterministic rule-based implementation.
Populated by Jules agent after rule inference.
"""

import json
from pathlib import Path

RULES_PATH = Path(__file__).parent.parent / "spec" / "rules.json"

def load_rules():
    with open(RULES_PATH, encoding="utf-8") as f:
        return json.load(f)

def transcribe(thai_word: str, rules: dict) -> str:
    raise NotImplementedError("Rule engine not yet implemented.")

if __name__ == "__main__":
    import sys
    rules = load_rules()
    word = sys.argv[1] if len(sys.argv) > 1 else ""
    print(transcribe(word, rules))
