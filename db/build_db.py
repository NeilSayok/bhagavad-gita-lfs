#!/usr/bin/env python3
"""Build db/gita.db from the chapter/ and slok/ JSON files, per db/schema.sql.

Usage: python3 db/build_db.py [--out db/gita.db]
Empty / whitespace-only translation strings are skipped: a missing row means
"not translated yet", so a later language drops in as pure INSERTs.
"""
import argparse
import glob
import json
import os
import re
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LANGUAGES = [
    # code, native name, English name, is_script_only
    ("sa", "संस्कृतम्", "Sanskrit", 1),
    ("hi", "हिन्दी", "Hindi", 0),
    ("en", "English", "English", 0),
    ("be", "বাংলা", "Bengali", 0),
    ("ka", "ಕನ್ನಡ", "Kannada", 0),
]

COMMENTATOR_ORDER = [
    "tej", "siva", "purohit", "chinmay", "san", "adi", "gambir", "madhav",
    "anand", "rams", "raman", "abhinav", "sankar", "jaya", "vallabh", "ms",
    "srid", "dhan", "venkat", "puru", "neel", "prabhu",
]


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def txt(v):
    return v.strip() if isinstance(v, str) and v.strip() else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "db", "gita.db"))
    args = ap.parse_args()

    if os.path.exists(args.out):
        os.remove(args.out)
    db = sqlite3.connect(args.out)
    db.executescript(open(os.path.join(ROOT, "db", "schema.sql")).read())
    db.execute("PRAGMA foreign_keys = ON")

    db.executemany("INSERT INTO language VALUES (?,?,?,?)", LANGUAGES)

    # ---- chapters -------------------------------------------------------
    for path in sorted(glob.glob(os.path.join(ROOT, "chapter", "*.json"))):
        c = json.load(open(path))
        n = c["chapter_number"]
        img = "chapters/chapter_%d/%s/img.jpeg" % (n, "%s")
        db.execute(
            "INSERT INTO chapter VALUES (?,?,?,?,?,?,?,?)",
            (n, c["verses_count"], c["name"], c["translation"], c["transliteration"],
             img % "landscape", img % "portrait", img % "square"),
        )
        for lang in set(c["meaning"]) | set(c["summary"]):
            meaning, summary = txt(c["meaning"].get(lang)), txt(c["summary"].get(lang))
            if meaning or summary:
                db.execute("INSERT INTO chapter_translation VALUES (?,?,?,?)",
                           (n, lang, meaning, summary))

    # ---- commentators (author normalized: most common spelling wins) ----
    authors = {}
    slok_files = sorted(glob.glob(os.path.join(ROOT, "slok", "*.json")))
    for path in slok_files:
        d = json.load(open(path))
        for key in COMMENTATOR_ORDER:
            a = txt((d.get(key) or {}).get("author"))
            if a:
                authors.setdefault(key, {})
                authors[key][a] = authors[key].get(a, 0) + 1
    for i, key in enumerate(COMMENTATOR_ORDER):
        best = max(authors.get(key, {"": 0}).items(), key=lambda kv: kv[1])[0]
        db.execute("INSERT INTO commentator VALUES (?,?,?)", (key, best, i))

    # ---- themes ---------------------------------------------------------
    theme_ids = {}
    for path in slok_files:
        for name in json.load(open(path))["themes"]:
            if name not in theme_ids:
                theme_ids[name] = len(theme_ids) + 1
    for name, tid in theme_ids.items():
        db.execute("INSERT INTO theme VALUES (?,?)", (tid, slugify(name)))
        db.execute("INSERT INTO theme_translation VALUES (?,?,?)", (tid, "en", name))

    # ---- verses ---------------------------------------------------------
    for path in slok_files:
        d = json.load(open(path))
        vid, ch, vn = d["_id"], d["chapter"], d["verse"]
        img = "sloks/chapter_%d/slok_%d/%s/img.jpeg" % (ch, vn, "%s")
        db.execute(
            "INSERT INTO verse VALUES (?,?,?,?,?,?,?)",
            (vid, ch, vn, d["transliteration"],
             img % "landscape", img % "portrait", img % "square"),
        )
        for lang in set(d["speaker"]) | set(d["slok"]):
            speaker, slok = txt(d["speaker"].get(lang)), txt(d["slok"].get(lang))
            if speaker or slok:
                db.execute("INSERT INTO verse_text VALUES (?,?,?,?)", (vid, lang, speaker, slok))

        if txt(d.get("life_application")):
            db.execute("INSERT INTO verse_translation VALUES (?,?,?)",
                       (vid, "en", d["life_application"].strip()))

        for pos, name in enumerate(d["themes"]):
            db.execute("INSERT INTO verse_theme VALUES (?,?,?)", (vid, theme_ids[name], pos))

        for pos, w in enumerate(d["word_meanings"]):
            db.execute("INSERT INTO word_meaning VALUES (?,?,?,?)",
                       (vid, pos, w["sanskrit"], w["transliteration"]))
            if txt(w["meaning"]):
                db.execute("INSERT INTO word_meaning_translation VALUES (?,?,?,?)",
                           (vid, pos, "en", w["meaning"].strip()))

        for key in COMMENTATOR_ORDER:
            for lang, text in (d.get(key) or {}).get("commentary", {}).items():
                if txt(text):
                    db.execute("INSERT INTO commentary VALUES (?,?,?,?)",
                               (vid, key, lang, text.strip()))

    db.execute("PRAGMA user_version = 1")  # bump to match Room's schema version
    db.commit()
    verify(db, len(slok_files))
    db.close()
    print("wrote %s (%.1f MB)" % (args.out, os.path.getsize(args.out) / 1e6))


def verify(db, n_sloks):
    q = lambda s: db.execute(s).fetchone()[0]
    assert q("SELECT count(*) FROM chapter") == 18
    assert q("SELECT count(*) FROM verse") == n_sloks
    assert q("SELECT count(*) FROM commentator") == 22
    # verse numbers are contiguous 1..N in every chapter (no gaps, no dupes).
    # N is verses_count + 1 for all 18 chapters — the JSON's verses_count uses a
    # different counting convention, so it is stored as-is and not asserted on.
    bad = db.execute(
        "SELECT chapter_number, count(*), min(verse_number), max(verse_number) FROM verse "
        "GROUP BY chapter_number HAVING min(verse_number) != 1 OR max(verse_number) != count(*)"
    ).fetchall()
    assert not bad, "non-contiguous verse numbering: %s" % bad
    # no orphans (foreign_keys was ON during insert, this catches schema gaps)
    assert not db.execute("PRAGMA foreign_key_check").fetchall()
    assert q("SELECT count(*) FROM commentary") > 0
    assert q("SELECT count(DISTINCT lang_code) FROM commentary") == 5
    print("ok: %d verses, %d commentary rows, %d word meanings, %d themes" % (
        q("SELECT count(*) FROM verse"), q("SELECT count(*) FROM commentary"),
        q("SELECT count(*) FROM word_meaning"), q("SELECT count(*) FROM theme")))


if __name__ == "__main__":
    sys.exit(main())
