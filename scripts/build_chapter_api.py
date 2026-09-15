"""Build api/chapter-slok/<number>/list.json (static, precomputed) from db/gita.db.
One file per chapter, containing all its verses.

Every text field is emitted as a {hi,en,be,ka} object, matching the source
JSON and db/schema.sql v2's per-language rows.
"""
import json
import os
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "db", "gita.db")
OUT_DIR = os.path.join(ROOT, "api", "chapter-slok")
LANGS = ("hi", "en", "be", "ka")

VERSE_QUERY = """
SELECT v.chapter_number, v.verse_id, v.img_landscape, v.img_square
FROM verse v
ORDER BY v.chapter_number, v.verse_number
"""

CHAPTER_TRANSLATION_QUERY = "SELECT chapter_number, lang_code, translation FROM chapter_translation"
VERSE_TEXT_QUERY = "SELECT verse_id, lang_code, speaker, slok, transliteration FROM verse_text"
VERSE_TRANSLATION_QUERY = "SELECT verse_id, lang_code, life_application FROM verse_translation"


def by_key(rows, key, *fields):
    """{key: {field: {lang: value}}} from per-language rows."""
    out = {}
    for r in rows:
        bucket = out.setdefault(r[key], {f: {} for f in fields})
        for f in fields:
            if r[f] is not None:
                bucket[f][r["lang_code"]] = r[f]
    return out


def ordered(values):
    return {lang: values[lang] for lang in LANGS if lang in values}


def main():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    verses = db.execute(VERSE_QUERY).fetchall()
    chapter_translations = by_key(
        db.execute(CHAPTER_TRANSLATION_QUERY).fetchall(), "chapter_number", "translation")
    verse_texts = by_key(
        db.execute(VERSE_TEXT_QUERY).fetchall(), "verse_id", "speaker", "slok", "transliteration")
    verse_translations = by_key(
        db.execute(VERSE_TRANSLATION_QUERY).fetchall(), "verse_id", "life_application")
    db.close()

    chapters = {}
    for r in verses:
        ch, vid = r["chapter_number"], r["verse_id"]
        text = verse_texts[vid]
        chapters.setdefault(ch, {
            "chapter": {"translation": ordered(chapter_translations[ch]["translation"])},
            "sloks": [],
        })["sloks"].append({
            "verse": {
                "verse_id": vid,
                "img_landscape": r["img_landscape"],
                "img_square": r["img_square"],
                "transliteration": ordered(text["transliteration"]),
            },
            "verse_text": {
                "speaker": ordered(text["speaker"]),
                "slok": ordered(text["slok"]),
            },
            "verse_translation": {
                "life_application": ordered(verse_translations[vid]["life_application"]),
            },
        })

    assert len(chapters) == 18, f"expected 18 chapters, got {len(chapters)}"

    for chapter_number, data in chapters.items():
        out_dir = os.path.join(OUT_DIR, str(chapter_number))
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "list.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        with open(out_path, encoding="utf-8") as f:
            json.load(f)  # round-trip validity check

    total_sloks = sum(len(d["sloks"]) for d in chapters.values())
    assert total_sloks == 701, f"expected 701 verses total, got {total_sloks}"
    print(f"wrote {len(chapters)} chapter files, {total_sloks} verses total, under {OUT_DIR}")


if __name__ == "__main__":
    main()
