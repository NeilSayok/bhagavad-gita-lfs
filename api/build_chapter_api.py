"""Build api/chapter/<number>/list.json (static, precomputed) from db/gita.db.
One file per chapter, containing all its verses.
"""
import json
import os
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "db", "gita.db")
OUT_DIR = os.path.join(ROOT, "api", "chapter")

QUERY = """
SELECT c.chapter_number, c.translation AS chapter_translation,
       v.verse_id, v.img_landscape, v.img_square, v.transliteration,
       vt.speaker, vt.slok,
       vtr.life_application
FROM verse v
JOIN chapter c ON c.chapter_number = v.chapter_number
LEFT JOIN verse_text vt ON vt.verse_id = v.verse_id AND vt.lang_code = 'hi'
LEFT JOIN verse_translation vtr ON vtr.verse_id = v.verse_id AND vtr.lang_code = 'en'
ORDER BY c.chapter_number, v.verse_number
"""


def main():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    rows = db.execute(QUERY).fetchall()
    db.close()

    chapters = {}
    for r in rows:
        chapters.setdefault(r["chapter_number"], {
            "chapter": {"translation": r["chapter_translation"]},
            "sloks": [],
        })["sloks"].append({
            "verse": {
                "verse_id": r["verse_id"],
                "img_landscape": r["img_landscape"],
                "img_square": r["img_square"],
                "transliteration": r["transliteration"],
            },
            "verse_text": {
                "speaker": r["speaker"],
                "slok": r["slok"],
            },
            "verse_translation": {
                "life_application": r["life_application"],
            },
        })

    assert len(chapters) == 18, f"expected 18 chapters, got {len(chapters)}"

    for chapter_number, data in chapters.items():
        out_dir = os.path.join(OUT_DIR, str(chapter_number))
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "list.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        with open(out_path, encoding="utf-8") as f:
            json.load(f)  # round-trip validity check

    total_sloks = sum(len(d["sloks"]) for d in chapters.values())
    assert total_sloks == 719, f"expected 719 verses total, got {total_sloks}"
    print(f"wrote {len(chapters)} chapter files, {total_sloks} verses total, under {OUT_DIR}")


if __name__ == "__main__":
    main()
