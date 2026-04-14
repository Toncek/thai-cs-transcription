# Konfigurácia pre Jules (AI Agent) - Thai SRS Content Pipeline

## Tvoja Úloha
Napíš Python skript (`generate_blocks.py`), ktorý načíta zdrojové dáta, prejde novú hierarchickú osnovu a vygeneruje jednotlivé JSON súbory pre každú kapitolu.
Tieto JSON súbory musia obsahovať aj informáciu o tom, do akého bloku patria, aby to Flutter aplikácia vedela jednoducho načítať.

## Zdroj dát
Použi výhradne súbor `data/train.json`.
Jeho štruktúra: `{"chapters": [ {"title": "Slovesa", "words": [ {"cz": "...", "sk": "...", "th": "...", "czph": "...", "skph": "..."} ]} ]}`.

## Výstupný formát (Jednotlivé JSON súbory)
Každá kapitola bude mať svoj vlastný JSON súbor (napr. `output/chapters/chapter_01.json`).
Formát musí presne zodpovedať tomuto vzoru (pridali sme `blockId`):
```json
{
  "id": 4,
  "blockId": 1,
  "name": "Přídavná jména",
  "orderIndex": 3,
  "words": [
    {
      "id": 142,
      "cz": "přídavná jména",
      "sk": "prídavné mená",
      "th": "คุณศัพท์",
      "czph": "khunasap",
      "skph": "khunasap"
    }
  ]
}
```

## Pravidlá a logika spracovania (KROK ZA KROKOM)

### 1. Príprava
- Načítaj `data/train.json` do pamäte a vytvor si mapu kapitol podľa `title`.
- Načítaj `curriculum.json`.
- Vytvor si globálne pole `learned_words_pool = []`. Do tohto poľa sa budú postupne sypať VŠETKY slovíčka, ktoré skript pridá do akýchkoľvek `vocab` kapitol naprieč všetkými blokmi. Tým zaručíme, že blok 4 si pamätá slová z bloku 1.

### 2. Vocab kapitoly (`type: "vocab"`)
- Prechádzaj `blocks` a v nich `chapters`.
- Ak je kapitola `vocab`, zober slovíčka zo zdrojov (`sources`) podľa `title`, `take`, `skip`.
- Vygeneruj pre každé slovo unikátne `id`.
- Zachovaj pôvodné hodnoty `cz`, `sk`, `th`, `czph`, `skph`.
- **Dôležité:** Každé takto pridané slovo (jeho originál aj preklad) okamžite nakopíruj do `learned_words_pool`.

### 3. Practice kapitoly (`type: "practice"`)
- Keď narazíš na vetnú kapitolu, zavolaj LLM  (OpenAI/Gemini).
- Do promptu vlož aktuálny stav `learned_words_pool`.
- **Inštrukcia pre LLM:** *"Vygeneruj X thajských viet (len th, sk, cz). Musíš použiť hlavne slová z predloženého zoznamu, aby si študent opakoval už naučené učivo."*
- **Generovanie výslovnosti (KRITICKÉ):** Keď ti LLM vráti vety (`th`), NESMIEŠ nechať LLM generovať fonetický prepis. Musíš importovať lokálny skript a vygenerovať to ním:
  ```python
  from src.transcriber import transcribe, load_rules
  rules = load_rules()
  ...
  czph = transcribe(sentence["th"], rules)
  skph = czph # skph nastav na rovnakú hodnotu ako czph
  ```
- Priraď vetám unikátne `id` a ulož ich do poľa `"words"` vo výstupnom JSONe danej kapitoly.

### 4. Ukladanie súborov
- Ulož každý výstup do zložky `output/chapters/` ako `chapter_01.json`, `chapter_02.json` atď.
- Pre aplikáciu vygeneruj aj pomocný súbor `output/blocks_index.json`, ktorý bude obsahovať len zoznam blokov a v nich len `id` kapitol (aby aplikácia vedela, v akom poradí a do akého bloku patria). Príklad:
  ```json
  [
    {
      "id": 1,
      "name": "Základy a prežitie",
      "chapters": [1, 2, 3, 4, 5]
    }
  ]
  ```

## Povinnosti
1. Žiadne `czph` generované umelou inteligenciou pre vety. Vždy sa volá `transcribe()`.
2. Do viet sa smú použiť hlavne slová z `learned_words_pool`.
3. Všetky kapitoly (vocab aj practice) majú rovnakú štruktúru poľa `"words"`.