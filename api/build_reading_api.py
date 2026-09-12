"""Build api/reading/all.json (static, precomputed) from db/gita.db, with a
colophon block appended after each chapter's verses (colophons are excluded
from db/gita.db, sourced directly from api/slok-colophon/*.json instead).
"""
import glob
import json
import os
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "db", "gita.db")
OUT_PATH = os.path.join(ROOT, "api", "reading", "all.json")
COLOPHON_DIR = os.path.join(ROOT, "api", "slok-colophon")

QUERY = """
SELECT v.verse_id, v.chapter_number, v.verse_number, v.transliteration,
       v.img_landscape, v.img_square,
       c.translation AS chapter_translation,
       vt.speaker, vt.slok,
       vtr.life_application
FROM verse v
JOIN chapter c ON c.chapter_number = v.chapter_number
LEFT JOIN verse_text vt ON vt.verse_id = v.verse_id AND vt.lang_code = 'hi'
LEFT JOIN verse_translation vtr ON vtr.verse_id = v.verse_id AND vtr.lang_code = 'en'
ORDER BY v.chapter_number, v.verse_number
"""


def load_colophons():
    """chapter_number -> colophon block, sourced from api/slok-colophon/*.json."""
    colophons = {}
    for path in glob.glob(os.path.join(COLOPHON_DIR, "*.json")):
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        colophons[d["chapter"]] = {
            "verse_id": d["_id"],
            "transliteration": d["transliteration"],
            "speaker": d["speaker"].get("hi"),
            "slok": d["slok"].get("hi"),
        }
    return colophons


def main():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    rows = db.execute(QUERY).fetchall()
    db.close()
    colophons = load_colophons()

    out = []
    prev_chapter = None
    for r in rows:
        ch = r["chapter_number"]
        if prev_chapter is not None and ch != prev_chapter:
            out.append({
                "chapter": {"translation": prev_translation},
                "colophon": colophons[prev_chapter],
            })
        out.append({
            "chapter": {
                "translation": r["chapter_translation"],
            },
            "verse": {
                "verse_id": r["verse_id"],
                "chapter_number": r["chapter_number"],
                "verse_number": r["verse_number"],
                "transliteration": r["transliteration"],
                "img_landscape": r["img_landscape"],
                "img_square": r["img_square"],
            },
            "verse_text": {
                "speaker": r["speaker"],
                "slok": r["slok"],
            },
            "verse_translation": {
                "life_application": r["life_application"],
            },
        })
        prev_chapter, prev_translation = ch, r["chapter_translation"]
    if prev_chapter is not None:
        out.append({
            "chapter": {"translation": prev_translation},
            "colophon": colophons[prev_chapter],
        })

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    verses = [o for o in out if "verse" in o]
    colophon_entries = [o for o in out if "colophon" in o]
    assert len(verses) == 701, f"expected 701 verses, got {len(verses)}"
    assert len(colophon_entries) == 18, f"expected 18 colophons, got {len(colophon_entries)}"
    ids = [o["verse"]["verse_id"] for o in verses]
    assert len(set(ids)) == len(ids), "duplicate verse_id"
    with open(OUT_PATH, encoding="utf-8") as f:
        json.load(f)  # round-trip validity check

    print(f"wrote {len(verses)} verses + {len(colophon_entries)} colophons to {OUT_PATH}")


if __name__ == "__main__":
    main()
