"""Randomizer: verse-of-the-day -> api/home/verseofday.json.

Verse itself is a fixed constant (mirrors HomeViewModel.kt's VERSE_OF_DAY_ID
"until a real per-day rotation exists") - only the commentator shown rotates,
by epoch day mod commentary count, same as the app's currentEpochDay() logic.
"""
import json
import os
import sqlite3
from datetime import date, timezone, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(ROOT, "db", "gita.db")
OUT_PATH = os.path.join(ROOT, "api", "home", "verseofday.json")

VERSE_OF_DAY_ID = "BG2.47"

VERSE_QUERY = """
SELECT v.verse_id, v.chapter_number, v.verse_number, v.transliteration,
       v.img_landscape, v.img_portrait, v.img_square,
       vtr.life_application
FROM verse v
LEFT JOIN verse_translation vtr ON vtr.verse_id = v.verse_id AND vtr.lang_code = 'en'
WHERE v.verse_id = ?
"""

VERSE_TEXT_QUERY = "SELECT speaker, slok FROM verse_text WHERE verse_id = ? AND lang_code = 'hi'"

COMMENTARY_QUERY = """
SELECT c.text, cm.author
FROM commentary c
JOIN commentator cm ON cm.commentator_key = c.commentator_key
WHERE c.verse_id = ? AND c.lang_code = 'en' AND c.text IS NOT NULL
ORDER BY cm.display_order
"""


def epoch_day():
    return (datetime.now(timezone.utc).date() - date(1970, 1, 1)).days


def main():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row

    v = db.execute(VERSE_QUERY, (VERSE_OF_DAY_ID,)).fetchone()
    assert v is not None, f"{VERSE_OF_DAY_ID} not found in verse table"
    vt = db.execute(VERSE_TEXT_QUERY, (VERSE_OF_DAY_ID,)).fetchone()
    commentary_rows = db.execute(COMMENTARY_QUERY, (VERSE_OF_DAY_ID,)).fetchall()
    db.close()

    if commentary_rows:
        chosen = commentary_rows[epoch_day() % len(commentary_rows)]
        daily_wisdom_text, daily_wisdom_author = chosen["text"], chosen["author"]
    else:
        daily_wisdom_text, daily_wisdom_author = v["life_application"], None

    out = {
        "verse": {
            "verse_id": v["verse_id"],
            "chapter_number": v["chapter_number"],
            "verse_number": v["verse_number"],
            "transliteration": v["transliteration"],
            "img_landscape": v["img_landscape"],
            "img_portrait": v["img_portrait"],
            "img_square": v["img_square"],
        },
        "verse_text": {
            "speaker": vt["speaker"] if vt else None,
            "slok": vt["slok"] if vt else None,
        },
        "verse_translation": {
            "life_application": v["life_application"],
        },
        "commentary": {
            "text": daily_wisdom_text,
        },
        "commentator": {
            "author": daily_wisdom_author,
        },
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    with open(OUT_PATH, encoding="utf-8") as f:
        json.load(f)  # round-trip validity check

    print(f"wrote verse of day ({VERSE_OF_DAY_ID}, commentator={daily_wisdom_author}) to {OUT_PATH}")


if __name__ == "__main__":
    main()
