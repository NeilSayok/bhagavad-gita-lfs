"""Randomizer: pick 10 random verses for the wisdom screen -> api/wisdom/daily.json.

Rules (per user):
  - commentary text shown on a card must be short: ~3-4 lines (character-length
    window, since raw commentary text has no hard line breaks).
  - never the same verse as api/home/verseofday.json (VERSE_OF_DAY_ID).
  - every text field (slok, life_application, commentary) must have all 4
    translations present (hi/en/be/ka) for whatever verse+commentator gets picked.

life_application has no per-language rows in db/gita.db (source JSON only ever
populated "en") -- api/reading/all.json is hand-translated with all 4 languages
and is the source of truth for that field now, read directly instead of the DB.
"""
import json
import os
import random
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(ROOT, "db", "gita.db")
READING_PATH = os.path.join(ROOT, "api", "reading", "all.json")
OUT_PATH = os.path.join(ROOT, "api", "wisdom", "daily.json")
COUNT = 10
LANGS = ("hi", "en", "be", "ka")

# mirrors verse_of_day.py's constant -- wisdom must never pick this verse
VERSE_OF_DAY_ID = "BG2.47"

MIN_CHARS, MAX_CHARS = 100, 260  # ~3-4 lines on a mobile card

VERSE_IDS_QUERY = "SELECT verse_id FROM verse WHERE verse_id != ?"

VERSE_QUERY = """
SELECT verse_id, chapter_number, verse_number, img_portrait
FROM verse WHERE verse_id = ?
"""

SLOK_QUERY = "SELECT lang_code, slok FROM verse_text WHERE verse_id = ? AND slok IS NOT NULL"

COMMENTARY_QUERY = """
SELECT cm.commentator_key, cm.author, c.lang_code, c.text
FROM commentary c
JOIN commentator cm ON cm.commentator_key = c.commentator_key
WHERE c.verse_id = ? AND c.text IS NOT NULL
ORDER BY cm.display_order
"""


def load_life_applications():
    with open(READING_PATH, encoding="utf-8") as f:
        entries = json.load(f)
    return {
        o["verse"]["verse_id"]: o["verse_translation"]["life_application"]
        for o in entries if "verse" in o
    }


def pick_commentary(db, verse_id):
    """First (by display_order) commentator with all 4 langs present and an
    English text length in the 3-4 line window. None if no such commentator."""
    rows = db.execute(COMMENTARY_QUERY, (verse_id,)).fetchall()
    by_commentator = {}
    for r in rows:
        by_commentator.setdefault(r["commentator_key"], {"author": r["author"], "text": {}})
        by_commentator[r["commentator_key"]]["text"][r["lang_code"]] = r["text"]

    for key, block in by_commentator.items():  # dict preserves insertion = display_order
        text = block["text"]
        if not all(lang in text for lang in LANGS):
            continue
        if not (MIN_CHARS <= len(text["en"]) <= MAX_CHARS):
            continue
        return block["author"], {lang: text[lang] for lang in LANGS}
    return None


def main():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    life_applications = load_life_applications()

    candidates = [r[0] for r in db.execute(VERSE_IDS_QUERY, (VERSE_OF_DAY_ID,)).fetchall()]
    random.shuffle(candidates)

    items = []
    for verse_id in candidates:
        if len(items) >= COUNT:
            break

        life_application = life_applications.get(verse_id)
        if not life_application or set(life_application) != set(LANGS):
            continue

        slok = {r["lang_code"]: r["slok"] for r in db.execute(SLOK_QUERY, (verse_id,)).fetchall()}
        if not all(lang in slok for lang in LANGS):
            continue

        picked = pick_commentary(db, verse_id)
        if picked is None:
            continue
        author, commentary_text = picked

        v = db.execute(VERSE_QUERY, (verse_id,)).fetchone()
        items.append({
            "verse": {
                "verse_id": v["verse_id"],
                "chapter_number": v["chapter_number"],
                "verse_number": v["verse_number"],
                "img_portrait": v["img_portrait"],
            },
            "verse_text": {
                "slok": {lang: slok[lang] for lang in LANGS},
            },
            "verse_translation": {
                "life_application": life_application,
            },
            "commentary": {
                "text": commentary_text,
            },
            "commentator": {
                "author": author,
            },
        })
    db.close()

    assert len(items) == COUNT, f"only found {len(items)}/{COUNT} qualifying verses"
    assert VERSE_OF_DAY_ID not in {i["verse"]["verse_id"] for i in items}

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    with open(OUT_PATH, encoding="utf-8") as f:
        json.load(f)  # round-trip validity check

    print(f"wrote {len(items)} random verses to {OUT_PATH}")


if __name__ == "__main__":
    main()
