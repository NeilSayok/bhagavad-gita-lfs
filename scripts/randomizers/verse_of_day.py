"""Randomizer: verse-of-the-day -> api/home/verseofday.json.

Both the verse and the commentator rotate daily, keyed on epoch day, so the file
is stable within a day and changes at the daily pipeline run. The verse is drawn
from a seed-shuffled list of eligible verses (see SHUFFLE_SEED), so re-running
the pipeline twice in one day produces an identical file (no spurious commits).

Rule (per user): every text field (slok, life_application, commentary) must have
all 4 translations present (hi/en/be/ka) for the verse and whichever commentator's
block gets rotated in.

wisdom_daily.py reads this file to avoid reusing today's verse, so this script must
run first -- the workflow's `for f in scripts/randomizers/*.py` loop is alphabetical,
which puts verse_of_day.py ahead of wisdom_daily.py.
"""
import json
import os
import random
import sqlite3
from datetime import date, timezone, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(ROOT, "db", "gita.db")
OUT_PATH = os.path.join(ROOT, "api", "home", "verseofday.json")
LANGS = ("hi", "en", "be", "ka")

SHUFFLE_SEED = 20260917

# Verses with all 4 languages on speaker, slok, transliteration and life_application.
ELIGIBLE_VERSES_QUERY = """
SELECT v.verse_id
FROM verse v
JOIN verse_text vt        ON vt.verse_id = v.verse_id AND vt.lang_code IN ('hi','en','be','ka')
JOIN verse_translation tr ON tr.verse_id = v.verse_id AND tr.lang_code IN ('hi','en','be','ka')
WHERE vt.speaker IS NOT NULL AND vt.slok IS NOT NULL
  AND vt.transliteration IS NOT NULL AND tr.life_application IS NOT NULL
GROUP BY v.verse_id
HAVING count(DISTINCT vt.lang_code) = 4 AND count(DISTINCT tr.lang_code) = 4
ORDER BY v.verse_id
"""

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


def pick_verse_of_day(db):
    """Today's verse: eligible ids shuffled by a fixed seed, indexed by epoch day."""
    ids = [r[0] for r in db.execute(ELIGIBLE_VERSES_QUERY).fetchall()]
    assert ids, "no verse has all 4 translations"
    random.Random(SHUFFLE_SEED).shuffle(ids)
    return ids[epoch_day() % len(ids)]


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

    verse_id = pick_verse_of_day(db)

    v = db.execute(VERSE_QUERY, (verse_id,)).fetchone()
    assert v is not None, f"{verse_id} not found in verse table"

    verse_text_rows = db.execute(VERSE_TEXT_QUERY, (verse_id,)).fetchall()
    speaker = {r["lang_code"]: r["speaker"] for r in verse_text_rows if r["speaker"]}
    slok = {r["lang_code"]: r["slok"] for r in verse_text_rows if r["slok"]}
    transliteration = {r["lang_code"]: r["transliteration"] for r in verse_text_rows
                       if r["transliteration"]}
    assert all(lang in speaker for lang in LANGS), "missing speaker translation"
    assert all(lang in slok for lang in LANGS), "missing slok translation"
    assert all(lang in transliteration for lang in LANGS), "missing transliteration"

    life_application = load_life_application(db, verse_id)
    assert all(lang in life_application for lang in LANGS), "missing life_application translation"

    candidates = qualifying_commentaries(db, verse_id)
    db.close()
    assert candidates, f"no fully-translated commentary found for {verse_id}"

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

    print(f"wrote verse of day ({verse_id}, commentator={author}) to {OUT_PATH}")


if __name__ == "__main__":
    main()
