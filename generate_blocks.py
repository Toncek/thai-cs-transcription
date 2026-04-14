import json
import os
import sys
import logging
from pathlib import Path
from openai import OpenAI

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Import transcriber
sys.path.insert(0, str(Path(__file__).parent))
from src.transcriber import transcribe, load_rules

# Constants
TRAIN_DATA_PATH = Path("data/train.json")
CURRICULUM_PATH = Path("anki/curriculum.json")
OUTPUT_DIR = Path("output")
CHAPTERS_OUT_DIR = OUTPUT_DIR / "chapters"
BLOCKS_INDEX_PATH = OUTPUT_DIR / "blocks_index.json"

def generate_practice_sentences(learned_words_pool, count):
    """Calls LLM to generate practice sentences."""
    # Build word list string for the prompt
    word_list = ", ".join([f"{w['th']} ({w['sk']}/{w['cz']})" for w in learned_words_pool])

    prompt = f"""Vygeneruj {count} thajských viet (len th, sk, cz vo formáte JSON). Musíš použiť hlavne slová z predloženého zoznamu, aby si študent opakoval už naučené učivo.

Zoznam slov:
{word_list}

Vráť výstup ako JSON pole objektov vnútri wrapper objektu. Formát musí byť presne takýto:
{{
  "sentences": [
    {{"th": "...", "sk": "...", "cz": "..."}},
    {{"th": "...", "sk": "...", "cz": "..."}}
  ]
}}"""

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.warning("No OPENAI_API_KEY found, generating mock sentences.")
        return [{"th": "mock thai", "sk": "mock slovak", "cz": "mock czech"} for _ in range(count)]

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful language learning assistant. Always reply with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        content = response.choices[0].message.content
        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict) and "sentences" in parsed:
                return parsed["sentences"]
            elif isinstance(parsed, list):
                return parsed
            elif isinstance(parsed, dict):
                # Try finding any list value
                for v in parsed.values():
                    if isinstance(v, list):
                        return v
            return parsed
        except Exception as e:
            logger.error(f"Failed to parse JSON: {content}")
            return []
    except Exception as e:
        logger.error(f"LLM API call failed: {e}")
        return []


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
                count = 15
                sentences = generate_practice_sentences(learned_words_pool, count)

                for s in sentences:
                    th_text = s.get("th", "")
                    czph = transcribe(th_text, rules)

                    new_word = {
                        "id": word_id_counter,
                        "cz": s.get("cz", ""),
                        "sk": s.get("sk", ""),
                        "th": th_text,
                        "czph": czph,
                        "skph": czph
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
