#!/usr/bin/env python3
"""Build db/gita.db from api/chapter/, api/slok/ and api/slok-colophon/, per db/schema.sql.

Usage: python3 db/build_db.py [--out db/gita.db] [--with-colophon]

Schema v2: the source JSON is fully multilingual -- chapter name/translation/
transliteration, verse speaker/slok/transliteration/life_application and
word-meaning transliteration/meaning are all {hi,en,be,ka} objects. Each lands
as one row per language in the matching *_translation / *_text table.

Empty / whitespace-only translation strings are skipped: a missing row means
"not translated yet", so a later language drops in as pure INSERTs.

Colophon verses (the closing "OM tatsat..." line, one per chapter) live in
api/slok-colophon/ and are excluded by default -- pass --with-colophon to
include them as regular verses.
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

# Theme names are English-only in the slok files; their translations are
# curated separately (db/theme_translations.json, keyed by slug).
THEME_TRANSLATIONS_PATH = os.path.join(ROOT, "db", "theme_translations.json")


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def txt(v):
    return v.strip() if isinstance(v, str) and v.strip() else None


def langs(field):
    """Non-blank {lang: text} from a multilingual source field.

    Tolerates a plain string (legacy, pre-multilingual files) by treating it
    as English-only, so a partially migrated tree still builds.
    """
    if isinstance(field, str):
        return {"en": field.strip()} if field.strip() else {}
    if isinstance(field, dict):
        return {lang: txt(v) for lang, v in field.items() if txt(v)}
    return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "db", "gita.db"))
    ap.add_argument("--with-colophon", action="store_true",
                    help="include api/slok-colophon/*.json as regular verses")
    args = ap.parse_args()

    out_dir = os.path.dirname(os.path.abspath(args.out))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    if os.path.exists(args.out):
        os.remove(args.out)
    db = sqlite3.connect(args.out)
    db.executescript(open(os.path.join(ROOT, "db", "schema.sql")).read())
    db.execute("PRAGMA foreign_keys = ON")

    db.executemany("INSERT INTO language VALUES (?,?,?,?)", LANGUAGES)

    # ---- chapters -------------------------------------------------------
    for path in sorted(glob.glob(os.path.join(ROOT, "api", "chapter", "*.json"))):
        c = json.load(open(path))
        n = c["chapter_number"]
        img = "chapters/{size}/chapter_%d/%s/img.png" % (n, "%s")
        db.execute(
            "INSERT INTO chapter VALUES (?,?,?,?,?)",
            (n, c["verses_count"], img % "landscape", img % "portrait", img % "square"),
        )
        fields = {f: langs(c.get(f)) for f in
                  ("name", "translation", "transliteration", "meaning", "summary")}
        for lang in set().union(*fields.values()):
            db.execute(
                "INSERT INTO chapter_translation VALUES (?,?,?,?,?,?,?)",
                (n, lang, fields["name"].get(lang), fields["translation"].get(lang),
                 fields["transliteration"].get(lang), fields["meaning"].get(lang),
                 fields["summary"].get(lang)),
            )

    # ---- commentators (author normalized: most common spelling wins) ----
    slok_files = sorted(glob.glob(os.path.join(ROOT, "api", "slok", "*.json")))
    if args.with_colophon:
        slok_files += sorted(glob.glob(os.path.join(ROOT, "api", "slok-colophon", "*.json")))

    authors = {}
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
    theme_names = json.load(open(THEME_TRANSLATIONS_PATH, encoding="utf-8"))
    theme_ids = {}
    for path in slok_files:
        for name in json.load(open(path))["themes"]:
            if name not in theme_ids:
                theme_ids[name] = len(theme_ids) + 1
    for name, tid in theme_ids.items():
        slug = slugify(name)
        db.execute("INSERT INTO theme VALUES (?,?)", (tid, slug))
        translations = theme_names.get(slug) or {"en": name}
        for lang, value in langs(translations).items():
            db.execute("INSERT INTO theme_translation VALUES (?,?,?)", (tid, lang, value))

    # ---- verses ---------------------------------------------------------
    for path in slok_files:
        d = json.load(open(path))
        vid, ch, vn = d["_id"], d["chapter"], d["verse"]
        img = "sloks/{size}/chapter_%d/slok_%d/%s/img.png" % (ch, vn, "%s")
        db.execute(
            "INSERT INTO verse VALUES (?,?,?,?,?,?)",
            (vid, ch, vn, img % "landscape", img % "portrait", img % "square"),
        )

        speaker, slok = langs(d.get("speaker")), langs(d.get("slok"))
        translit = langs(d.get("transliteration"))
        for lang in set(speaker) | set(slok) | set(translit):
            db.execute("INSERT INTO verse_text VALUES (?,?,?,?,?)",
                       (vid, lang, speaker.get(lang), slok.get(lang), translit.get(lang)))

        for lang, value in langs(d.get("life_application")).items():
            db.execute("INSERT INTO verse_translation VALUES (?,?,?)", (vid, lang, value))

        for pos, name in enumerate(d["themes"]):
            db.execute("INSERT INTO verse_theme VALUES (?,?,?)", (vid, theme_ids[name], pos))

        for pos, w in enumerate(d["word_meanings"]):
            db.execute("INSERT INTO word_meaning VALUES (?,?,?)", (vid, pos, w["sanskrit"]))
            wt, wm = langs(w.get("transliteration")), langs(w.get("meaning"))
            for lang in set(wt) | set(wm):
                db.execute("INSERT INTO word_meaning_translation VALUES (?,?,?,?,?)",
                           (vid, pos, lang, wt.get(lang), wm.get(lang)))

        for key in COMMENTATOR_ORDER:
            block = (d.get(key) or {}).get("commentary", {})
            for lang, text in langs(block).items():
                db.execute("INSERT INTO commentary VALUES (?,?,?,?)", (vid, key, lang, text))

    db.execute("PRAGMA user_version = 2")  # bump to match Room's schema version
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
    # Colophon verses (verses_count + 1) are excluded unless --with-colophon.
    bad = db.execute(
        "SELECT chapter_number, count(*), min(verse_number), max(verse_number) FROM verse "
        "GROUP BY chapter_number HAVING min(verse_number) != 1 OR max(verse_number) != count(*)"
    ).fetchall()
    assert not bad, "non-contiguous verse numbering: %s" % bad
    # no orphans (foreign_keys was ON during insert, this catches schema gaps)
    assert not db.execute("PRAGMA foreign_key_check").fetchall()
    assert q("SELECT count(*) FROM commentary") > 0
    assert q("SELECT count(DISTINCT lang_code) FROM commentary") == 5

    # every translated table carries all 4 target languages, not just English
    for table in ("chapter_translation", "verse_text", "verse_translation",
                  "theme_translation", "word_meaning_translation"):
        got = {r[0] for r in db.execute("SELECT DISTINCT lang_code FROM %s" % table)}
        assert {"hi", "en", "be", "ka"} <= got, "%s missing languages: %s" % (table, got)

    print("ok: %d verses, %d commentary rows, %d word meanings, %d themes" % (
        q("SELECT count(*) FROM verse"), q("SELECT count(*) FROM commentary"),
        q("SELECT count(*) FROM word_meaning"), q("SELECT count(*) FROM theme")))
    for table in ("chapter_translation", "verse_text", "verse_translation",
                  "theme_translation", "word_meaning_translation", "commentary"):
        rows = db.execute(
            "SELECT lang_code, count(*) FROM %s GROUP BY lang_code ORDER BY lang_code" % table
        ).fetchall()
        print("    %-26s %s" % (table, ", ".join("%s=%d" % r for r in rows)))


if __name__ == "__main__":
    sys.exit(main())
