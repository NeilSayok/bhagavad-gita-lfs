"""Build api/reading/all.json (static, precomputed) from db/gita.db, with a
colophon block appended after each chapter's verses (colophons are excluded
from db/gita.db, sourced directly from api/slok-colophon/*.json instead).

Every text field is emitted as a {hi,en,be,ka} object, matching the source
JSON and db/schema.sql v2's per-language rows.
"""
import glob
import json
import os
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "db", "gita.db")
OUT_PATH = os.path.join(ROOT, "api", "reading", "all.json")
COLOPHON_DIR = os.path.join(ROOT, "api", "slok-colophon")
LANGS = ("hi", "en", "be", "ka")

VERSE_QUERY = """
SELECT v.verse_id, v.chapter_number, v.verse_number, v.img_landscape, v.img_square
FROM verse v
ORDER BY v.chapter_number, v.verse_number
"""

CHAPTER_TRANSLATION_QUERY = """
SELECT chapter_number, lang_code, translation FROM chapter_translation
"""

VERSE_TEXT_QUERY = """
SELECT verse_id, lang_code, speaker, slok, transliteration FROM verse_text
"""

VERSE_TRANSLATION_QUERY = """
SELECT verse_id, lang_code, life_application FROM verse_translation
"""


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


def load_colophons():
    """chapter_number -> colophon block, sourced from api/slok-colophon/*.json."""
    colophons = {}
    for path in glob.glob(os.path.join(COLOPHON_DIR, "*.json")):
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        colophons[d["chapter"]] = {
            "verse_id": d["_id"],
            "transliteration": ordered(d["transliteration"]),
            "speaker": ordered(d["speaker"]),
            "slok": ordered(d["slok"]),
        }
    return colophons


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
    colophons = load_colophons()

    def chapter_block(chapter_number):
        return {"translation": ordered(chapter_translations[chapter_number]["translation"])}

    out = []
    prev_chapter = None
    for r in verses:
        ch, vid = r["chapter_number"], r["verse_id"]
        if prev_chapter is not None and ch != prev_chapter:
            out.append({
                "chapter": chapter_block(prev_chapter),
                "colophon": colophons[prev_chapter],
            })
        text = verse_texts[vid]
        out.append({
            "chapter": chapter_block(ch),
            "verse": {
                "verse_id": vid,
                "chapter_number": ch,
                "verse_number": r["verse_number"],
                "transliteration": ordered(text["transliteration"]),
                "img_landscape": r["img_landscape"],
                "img_square": r["img_square"],
            },
            "verse_text": {
                "speaker": ordered(text["speaker"]),
                "slok": ordered(text["slok"]),
            },
            "verse_translation": {
                "life_application": ordered(verse_translations[vid]["life_application"]),
            },
        })
        prev_chapter = ch
    if prev_chapter is not None:
        out.append({
            "chapter": chapter_block(prev_chapter),
            "colophon": colophons[prev_chapter],
        })

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")

    verse_entries = [o for o in out if "verse" in o]
    colophon_entries = [o for o in out if "colophon" in o]
    assert len(verse_entries) == 701, f"expected 701 verses, got {len(verse_entries)}"
    assert len(colophon_entries) == 18, f"expected 18 colophons, got {len(colophon_entries)}"
    ids = [o["verse"]["verse_id"] for o in verse_entries]
    assert len(set(ids)) == len(ids), "duplicate verse_id"
    for o in verse_entries:
        assert set(o["verse_text"]["slok"]) == set(LANGS), f"{o['verse']['verse_id']} slok langs"
        assert set(o["verse_translation"]["life_application"]) == set(LANGS), \
            f"{o['verse']['verse_id']} life_application langs"
    with open(OUT_PATH, encoding="utf-8") as f:
        json.load(f)  # round-trip validity check

    print(f"wrote {len(verse_entries)} verses + {len(colophon_entries)} colophons to {OUT_PATH}")


if __name__ == "__main__":
    main()
