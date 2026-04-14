import sys
import os
import json
import datetime

# Add parent directory to path so we can import src.transcriber
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.transcriber import transcribe, load_rules
from anki.chapters_definitions import CHAPTERS

def main():
    rules = load_rules()
    warnings = []
    summary = []

    os.makedirs("anki/chapters", exist_ok=True)

    for chapter in CHAPTERS:
        chapter_id = f"{chapter['chapter_id']:02d}"

        # Process words
        for word in chapter["words"]:
            czph = transcribe(word["th"], rules)
            word["czph"] = czph
            if "?" in czph:
                warnings.append({"type": "word", "th": word["th"], "czph": czph, "chapter": chapter_id})

        # Process sentences
        for sentence in chapter["sentences"]:
            czph = transcribe(sentence["th"], rules)
            sentence["czph"] = czph
            if "?" in czph:
                warnings.append({"type": "sentence", "th": sentence["th"], "czph": czph, "chapter": chapter_id})

        # Save chapter
        filename = f"anki/chapters/chapter_{chapter_id}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(chapter, f, ensure_ascii=False, indent=2)

        summary.append({
            "chapter": chapter_id,
            "title": chapter["title_cz"],
            "words": len(chapter["words"]),
            "sentences": len(chapter["sentences"]),
            "warnings": sum(1 for w in warnings if w["chapter"] == chapter_id)
        })

    # Save warnings
    with open("anki/transcription_warnings.json", "w", encoding="utf-8") as f:
        json.dump(warnings, f, ensure_ascii=False, indent=2)

    # Save summary markdown
    with open("anki/chapters_summary.md", "w", encoding="utf-8") as f:
        f.write(f"Regenerated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Warnings: {len(warnings)}\n\n")
        f.write("# Chapters Summary\n\n")
        f.write("| Chapter | Title | Words | Sentences | Warnings |\n")
        f.write("|---------|-------|-------|-----------|----------|\n")
        for s in summary:
            f.write(f"| {s['chapter']} | {s['title']} | {s['words']} | {s['sentences']} | {s['warnings']} |\n")

if __name__ == "__main__":
    main()
