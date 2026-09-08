"""Build api/reading/all.json (static, precomputed) from db/gita.db."""
import json
import os
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "db", "gita.db")
OUT_PATH = os.path.join(ROOT, "api", "reading", "all.json")

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


def main():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    rows = db.execute(QUERY).fetchall()
    db.close()

    out = []
    for r in rows:
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

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    assert len(out) == 719, f"expected 719 verses, got {len(out)}"
    ids = [o["verse"]["verse_id"] for o in out]
    assert len(set(ids)) == len(ids), "duplicate verse_id"
    with open(OUT_PATH, encoding="utf-8") as f:
        json.load(f)  # round-trip validity check

    print(f"wrote {len(out)} verses to {OUT_PATH}")


if __name__ == "__main__":
    main()
