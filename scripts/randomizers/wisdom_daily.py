"""Randomizer: pick 10 random verses for the wisdom screen -> api/wisdom/daily.json.

Self-contained: knows its own DB source and output path. The GitHub workflow
just discovers and runs every script under scripts/randomizers/.
"""
import json
import os
import random
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(ROOT, "db", "gita.db")
OUT_PATH = os.path.join(ROOT, "api", "wisdom", "daily.json")
COUNT = 10

VERSE_IDS_QUERY = "SELECT verse_id FROM verse"

VERSE_QUERY = """
SELECT v.verse_id, v.chapter_number, v.verse_number, v.img_portrait,
       vtr.life_application
FROM verse v
LEFT JOIN verse_translation vtr ON vtr.verse_id = v.verse_id AND vtr.lang_code = 'en'
WHERE v.verse_id = ?
"""

SLOK_QUERY = "SELECT lang_code, slok FROM verse_text WHERE verse_id = ? AND slok IS NOT NULL"

COMMENTARY_QUERY = """
SELECT c.text FROM commentary c
JOIN commentator cm ON cm.commentator_key = c.commentator_key
WHERE c.verse_id = ? AND c.lang_code = 'en' AND c.text IS NOT NULL
ORDER BY cm.display_order
LIMIT 1
"""


def main():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row

    all_ids = [r[0] for r in db.execute(VERSE_IDS_QUERY).fetchall()]
    chosen = random.sample(all_ids, COUNT)

    items = []
    for verse_id in chosen:
        v = db.execute(VERSE_QUERY, (verse_id,)).fetchone()
        slok = {r["lang_code"]: r["slok"] for r in db.execute(SLOK_QUERY, (verse_id,)).fetchall()}
        commentary_row = db.execute(COMMENTARY_QUERY, (verse_id,)).fetchone()

        items.append({
            "verse": {
                "verse_id": v["verse_id"],
                "chapter_number": v["chapter_number"],
                "verse_number": v["verse_number"],
                "img_portrait": v["img_portrait"],
            },
            "verse_text": {
                "slok": slok,
            },
            "verse_translation": {
                "life_application": v["life_application"],
            },
            "commentary": {
                "text": commentary_row["text"] if commentary_row else None,
            },
        })
    db.close()

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    assert len(items) == COUNT
    with open(OUT_PATH, encoding="utf-8") as f:
        json.load(f)  # round-trip validity check

    print(f"wrote {len(items)} random verses to {OUT_PATH}")


if __name__ == "__main__":
    main()
