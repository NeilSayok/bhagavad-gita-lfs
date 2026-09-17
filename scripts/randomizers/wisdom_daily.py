"""Randomizer: pick 10 random verses for the wisdom screen -> api/wisdom/daily.json.

Rules (per user):
  - commentary text shown on a card must be short: ~3-4 lines. Enforced as a
    character window applied to EVERY language, not just English -- Devanagari,
    Bengali and Kannada renderings of the same passage differ in length, so
    checking only `en` lets a much longer hi/be/ka text through.
  - never the same verse as api/home/verseofday.json -- that file is read at
    runtime (verse_of_day.py runs first; the workflow's glob loop is alphabetical).
  - every text field (slok, life_application, commentary) must have all 4
    translations present (hi/en/be/ka) for whatever verse+commentator gets picked.
"""
import json
import os
import random
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(ROOT, "db", "gita.db")
VERSE_OF_DAY_PATH = os.path.join(ROOT, "api", "home", "verseofday.json")
OUT_PATH = os.path.join(ROOT, "api", "wisdom", "daily.json")
COUNT = 10
LANGS = ("hi", "en", "be", "ka")

MIN_CHARS, MAX_CHARS = 90, 200  # ~3-4 lines on a mobile card, per language

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

LIFE_APPLICATION_QUERY = """
SELECT verse_id, lang_code, life_application FROM verse_translation
WHERE life_application IS NOT NULL
"""


def verse_of_day_id():
    """Today's verse-of-the-day, so wisdom never duplicates it."""
    with open(VERSE_OF_DAY_PATH, encoding="utf-8") as f:
        return json.load(f)["verse"]["verse_id"]


def load_life_applications(db):
    out = {}
    for r in db.execute(LIFE_APPLICATION_QUERY).fetchall():
        out.setdefault(r["verse_id"], {})[r["lang_code"]] = r["life_application"]
    return out


def pick_commentary(db, verse_id):
    """First (by display_order) commentator with all 4 langs present and every
    language's text inside the 3-4 line window. None if no such commentator."""
    rows = db.execute(COMMENTARY_QUERY, (verse_id,)).fetchall()
    by_commentator = {}
    for r in rows:
        by_commentator.setdefault(r["commentator_key"], {"author": r["author"], "text": {}})
        by_commentator[r["commentator_key"]]["text"][r["lang_code"]] = r["text"]

    for block in by_commentator.values():  # dict preserves insertion = display_order
        text = block["text"]
        if not all(lang in text for lang in LANGS):
            continue
        if not all(MIN_CHARS <= len(text[lang]) <= MAX_CHARS for lang in LANGS):
            continue
        return block["author"], {lang: text[lang] for lang in LANGS}
    return None


def main():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    life_applications = load_life_applications(db)
    excluded = verse_of_day_id()

    candidates = [r[0] for r in db.execute(VERSE_IDS_QUERY, (excluded,)).fetchall()]
    random.shuffle(candidates)

    items = []
    for verse_id in candidates:
        if len(items) >= COUNT:
            break

        life_application = life_applications.get(verse_id)
        if not life_application or not all(lang in life_application for lang in LANGS):
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
                "life_application": {lang: life_application[lang] for lang in LANGS},
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
    assert excluded not in {i["verse"]["verse_id"] for i in items}, \
        f"wisdom reused the verse of the day ({excluded})"
    for i in items:
        for lang, text in i["commentary"]["text"].items():
            assert MIN_CHARS <= len(text) <= MAX_CHARS, \
                f"{i['verse']['verse_id']} {lang} commentary is {len(text)} chars"

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
        f.write("\n")
    with open(OUT_PATH, encoding="utf-8") as f:
        json.load(f)  # round-trip validity check

    print(f"wrote {len(items)} random verses to {OUT_PATH} (excluded {excluded})")


if __name__ == "__main__":
    main()
