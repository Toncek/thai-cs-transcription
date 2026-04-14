import json
import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Import transcriber
sys.path.insert(0, str(Path(__file__).parent))
from src.transcriber import transcribe, load_rules

# Constants
TRAIN_DATA_PATH = Path("data/train.json")
CURRICULUM_PATH = Path("anki/curriculum.json")
PRACTICE_SENTENCES_PATH = Path("data/practice_sentences.json")
OUTPUT_DIR = Path("output")
CHAPTERS_OUT_DIR = OUTPUT_DIR / "chapters"
BLOCKS_INDEX_PATH = OUTPUT_DIR / "blocks_index.json"

def get_practice_sentences(chapter_id, count):
    """Loads pre-generated practice sentences for the given chapter."""
    if not PRACTICE_SENTENCES_PATH.exists():
        logger.warning(f"{PRACTICE_SENTENCES_PATH} not found.")
        return [{"th": "mock thai", "sk": "mock slovak", "cz": "mock czech"} for _ in range(count)]

    try:
        with open(PRACTICE_SENTENCES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        sentences = data.get(str(chapter_id), [])
        if not sentences:
            logger.warning(f"No sentences found for chapter {chapter_id} in {PRACTICE_SENTENCES_PATH}.")
            return [{"th": "mock thai", "sk": "mock slovak", "cz": "mock czech"} for _ in range(count)]

        return sentences[:count]
    except Exception as e:
        logger.error(f"Failed to load practice sentences: {e}")
        return [{"th": "mock thai", "sk": "mock slovak", "cz": "mock czech"} for _ in range(count)]

def main():
    CHAPTERS_OUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(TRAIN_DATA_PATH, "r", encoding="utf-8") as f:
        train_data = json.load(f)

    train_chapters_map = {ch["title"]: ch for ch in train_data.get("chapters", [])}

    with open(CURRICULUM_PATH, "r", encoding="utf-8") as f:
        curriculum = json.load(f)

    learned_words_pool = []
    rules = load_rules()

    word_id_counter = 1
    blocks_index = []

    for block in curriculum.get("blocks", []):
        block_id = block["id"]
        block_name = block["name"]

        block_info = {
            "id": block_id,
            "name": block_name,
            "chapters": []
        }

        for chapter_idx, chapter in enumerate(block.get("chapters", [])):
            chapter_id = chapter["id"]
            chapter_type = chapter.get("type", "vocab")
            chapter_name = chapter["name"]

            block_info["chapters"].append(chapter_id)

            output_words = []

            if chapter_type == "vocab":
                sources = chapter.get("sources", [])
                for source in sources:
                    title = source["title"]
                    take = source.get("take", "all")
                    skip = source.get("skip", 0)

                    if title in train_chapters_map:
                        source_words = train_chapters_map[title].get("words", [])

                        start_idx = skip
                        if take == "all":
                            selected_words = source_words[start_idx:]
                        else:
                            selected_words = source_words[start_idx : start_idx + int(take)]

                        for w in selected_words:
                            new_word = {
                                "id": word_id_counter,
                                "cz": w["cz"],
                                "sk": w["sk"],
                                "th": w["th"],
                                "czph": w["czph"],
                                "skph": w["skph"]
                            }
                            word_id_counter += 1
                            output_words.append(new_word)
                            # Add to learned words pool
                            learned_words_pool.append(new_word)
                    else:
                        logger.warning(f"Source chapter '{title}' not found in train.json")

            elif chapter_type == "practice":
                count = 15 # Strict instruction
                sentences = get_practice_sentences(chapter_id, count)

                for s in sentences:
                    th_text = s.get("th", "")
                    czph = transcribe(th_text, rules)

                    new_word = {
                        "id": word_id_counter,
                        "cz": s.get("cz", ""),
                        "sk": s.get("sk", ""),
                        "th": th_text,
                        "czph": czph,
                        "skph": czph # skph is set to czph as requested
                    }
                    word_id_counter += 1
                    output_words.append(new_word)

            # Create chapter output
            chapter_output = {
                "id": chapter_id,
                "blockId": block_id,
                "name": chapter_name,
                "orderIndex": chapter_idx,
                "words": output_words
            }

            # Save chapter JSON
            out_filename = CHAPTERS_OUT_DIR / f"chapter_{chapter_id:03d}.json"
            with open(out_filename, "w", encoding="utf-8") as f:
                json.dump(chapter_output, f, ensure_ascii=False, indent=2)

            logger.info(f"Saved {out_filename} with {len(output_words)} words/sentences.")

        blocks_index.append(block_info)

    # Save blocks index
    with open(BLOCKS_INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(blocks_index, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved {BLOCKS_INDEX_PATH}")

if __name__ == "__main__":
    main()
