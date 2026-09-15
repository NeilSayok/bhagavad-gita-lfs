"""Randomizer: verse-of-the-day -> api/home/verseofday.json.

Verse itself is a fixed constant (mirrors HomeViewModel.kt's VERSE_OF_DAY_ID
"until a real per-day rotation exists") - only the commentator shown rotates,
by epoch day mod commentary count, same as the app's currentEpochDay() logic.

Rule (per user): every text field (slok, life_application, commentary) must
have all 4 translations present (hi/en/be/ka) for the verse and whichever
commentator's block gets rotated in.
"""
import json
import os
import sqlite3
from datetime import date, timezone, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(ROOT, "db", "gita.db")
OUT_PATH = os.path.join(ROOT, "api", "home", "verseofday.json")
LANGS = ("hi", "en", "be", "ka")

VERSE_OF_DAY_ID = "BG2.47"

VERSE_QUERY = """
SELECT v.verse_id, v.chapter_number, v.verse_number,
       v.img_landscape, v.img_portrait, v.img_square
FROM verse v
WHERE v.verse_id = ?
"""

VERSE_TEXT_QUERY = """
SELECT lang_code, speaker, slok, transliteration FROM verse_text WHERE verse_id = ?
"""

LIFE_APPLICATION_QUERY = """
SELECT lang_code, life_application FROM verse_translation
WHERE verse_id = ? AND life_application IS NOT NULL
"""

COMMENTARY_QUERY = """
SELECT cm.commentator_key, cm.author, cm.display_order, c.lang_code, c.text
FROM commentary c
JOIN commentator cm ON cm.commentator_key = c.commentator_key
WHERE c.verse_id = ? AND c.text IS NOT NULL
ORDER BY cm.display_order
"""


def epoch_day():
    return (datetime.now(timezone.utc).date() - date(1970, 1, 1)).days


def load_life_application(db, verse_id):
    rows = db.execute(LIFE_APPLICATION_QUERY, (verse_id,)).fetchall()
    return {r["lang_code"]: r["life_application"] for r in rows}


def qualifying_commentaries(db, verse_id):
    """Commentators (in display_order) with all 4 langs present, keeping order."""
    rows = db.execute(COMMENTARY_QUERY, (verse_id,)).fetchall()
    by_commentator = {}
    for r in rows:
        by_commentator.setdefault(r["commentator_key"], {"author": r["author"], "text": {}})
        by_commentator[r["commentator_key"]]["text"][r["lang_code"]] = r["text"]
    return [
        (block["author"], {lang: block["text"][lang] for lang in LANGS})
        for block in by_commentator.values()
        if all(lang in block["text"] for lang in LANGS)
    ]


def main():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row

    v = db.execute(VERSE_QUERY, (VERSE_OF_DAY_ID,)).fetchone()
    assert v is not None, f"{VERSE_OF_DAY_ID} not found in verse table"

    verse_text_rows = db.execute(VERSE_TEXT_QUERY, (VERSE_OF_DAY_ID,)).fetchall()
    speaker = {r["lang_code"]: r["speaker"] for r in verse_text_rows if r["speaker"]}
    slok = {r["lang_code"]: r["slok"] for r in verse_text_rows if r["slok"]}
    transliteration = {r["lang_code"]: r["transliteration"] for r in verse_text_rows
                       if r["transliteration"]}
    assert all(lang in speaker for lang in LANGS), "missing speaker translation"
    assert all(lang in slok for lang in LANGS), "missing slok translation"
    assert all(lang in transliteration for lang in LANGS), "missing transliteration"

    life_application = load_life_application(db, VERSE_OF_DAY_ID)
    assert all(lang in life_application for lang in LANGS), "missing life_application translation"

    candidates = qualifying_commentaries(db, VERSE_OF_DAY_ID)
    db.close()
    assert candidates, f"no fully-translated commentary found for {VERSE_OF_DAY_ID}"

    author, commentary_text = candidates[epoch_day() % len(candidates)]

    out = {
        "verse": {
            "verse_id": v["verse_id"],
            "chapter_number": v["chapter_number"],
            "verse_number": v["verse_number"],
            "transliteration": {lang: transliteration[lang] for lang in LANGS},
            "img_landscape": v["img_landscape"],
            "img_portrait": v["img_portrait"],
            "img_square": v["img_square"],
        },
        "verse_text": {
            "speaker": {lang: speaker[lang] for lang in LANGS},
            "slok": {lang: slok[lang] for lang in LANGS},
        },
        "verse_translation": {
            "life_application": {lang: life_application[lang] for lang in LANGS},
        },
        "commentary": {
            "text": commentary_text,
        },
        "commentator": {
            "author": author,
        },
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")
    with open(OUT_PATH, encoding="utf-8") as f:
        json.load(f)  # round-trip validity check

    print(f"wrote verse of day ({VERSE_OF_DAY_ID}, commentator={author}) to {OUT_PATH}")


if __name__ == "__main__":
    main()
