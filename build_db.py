#!/usr/bin/env python3
"""Build gita.db (Room-compatible, prepopulated) from the chapter/ and slok/ JSON dataset.

Schema v2: all per-language text is row-per-language (chapter_translation,
verse_translation, commentary) so future languages are row inserts, and a
language pack = all rows WHERE lang='X'. Image columns are NULL provisions.

Run: python3 build_db.py
Output: gita.db in the repo root, plus a full round-trip losslessness check.
"""

import glob
import json
import os
import sqlite3
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOT, "gita.db")
SCHEMA_PATH = os.path.join(ROOT, "schema.sql")

LANGS = ("hi", "en", "be", "ka", "sa")  # canonical key order in source JSON

# Canonical commentator order + author names. Order is the key order in the source
# JSON files; author names are canonicalised here because two slok files omit the
# `author` key entirely and `prabhu` appears under two spellings.
COMMENTATORS = [
    ("tej", "Swami Tejomayananda"),
    ("siva", "Swami Sivananda"),
    ("purohit", "Shri Purohit Swami"),
    ("chinmay", "Swami Chinmayananda"),
    ("san", "Dr.S.Sankaranarayan"),
    ("adi", "Swami Adidevananda"),
    ("gambir", "Swami Gambirananda"),
    ("madhav", "Sri Madhavacharya"),
    ("anand", "Sri Anandgiri"),
    ("rams", "Swami Ramsukhdas"),
    ("raman", "Sri Ramanuja"),
    ("abhinav", "Sri Abhinav Gupta"),
    ("sankar", "Sri Shankaracharya"),
    ("jaya", "Sri Jayatritha"),
    ("vallabh", "Sri Vallabhacharya"),
    ("ms", "Sri Madhusudan Saraswati"),
    ("srid", "Sri Sridhara Swami"),
    ("dhan", "Sri Dhanpati"),
    ("venkat", "Vedantadeshikacharya Venkatanatha"),
    ("puru", "Sri Purushottamji"),
    ("neel", "Sri Neelkanth"),
    ("prabhu", "A.C. Bhaktivedanta Swami Prabhupada"),
]
COMMENTATOR_IDS = [c[0] for c in COMMENTATORS]


def verse_pk(chapter, verse):
    """Stable INTEGER rowid: chapter * 1000 + verse. Needed as a rowid alias so the
    external-content FTS tables and Room's @Fts4(contentEntity=...) can link by rowid."""
    return chapter * 1000 + verse


def build():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    con = sqlite3.connect(DB_PATH)
    con.executescript(open(SCHEMA_PATH, encoding="utf-8").read())

    con.executemany(
        "INSERT INTO commentator (id, author_name, sort_order, image) VALUES (?, ?, ?, NULL)",
        [(cid, name, i) for i, (cid, name) in enumerate(COMMENTATORS)],
    )

    # --- chapters + chapter translations ---
    chapter_files = sorted(
        glob.glob(os.path.join(ROOT, "chapter", "*.json")),
        key=lambda p: json.load(open(p, encoding="utf-8"))["chapter_number"],
    )
    for path in chapter_files:
        d = json.load(open(path, encoding="utf-8"))
        con.execute(
            """INSERT INTO chapter (chapter_number, verses_count, name_sa, translation,
                                    transliteration, image_square, image_landscape, image_portrait)
               VALUES (?, ?, ?, ?, ?, NULL, NULL, NULL)""",
            (d["chapter_number"], d["verses_count"], d["name"], d["translation"], d["transliteration"]),
        )
        langs = [l for l in LANGS if l in d["meaning"]]
        assert set(langs) == set(d["meaning"].keys()) == set(d["summary"].keys()), path
        con.executemany(
            "INSERT INTO chapter_translation (chapter, lang, meaning, summary) VALUES (?, ?, ?, ?)",
            [(d["chapter_number"], l, d["meaning"][l], d["summary"][l]) for l in langs],
        )

    # --- verses + verse translations + commentary ---
    slok_files = sorted(glob.glob(os.path.join(ROOT, "slok", "*.json")))
    verse_rows, vt_rows, commentary_rows = [], [], []
    for path in slok_files:
        d = json.load(open(path, encoding="utf-8"))
        ch, vs = d["chapter"], d["verse"]
        vid = verse_pk(ch, vs)
        verse_rows.append((vid, d["_id"], ch, vs, d["transliteration"]))
        langs = [l for l in LANGS if l in d["slok"]]
        assert set(langs) == set(d["slok"].keys()) == set(d["speaker"].keys()), path
        for l in langs:
            vt_rows.append((vid, l, d["speaker"][l], d["slok"][l]))
        for cid in COMMENTATOR_IDS:
            for lang, text in d[cid]["commentary"].items():
                commentary_rows.append((vid, cid, lang, text))

    con.executemany(
        """INSERT INTO verse (id, ext_id, chapter, verse_number, transliteration,
                              image_square, image_landscape, image_portrait)
           VALUES (?, ?, ?, ?, ?, NULL, NULL, NULL)""",
        verse_rows,
    )
    con.executemany(
        "INSERT INTO verse_translation (verse_id, lang, speaker, slok) VALUES (?, ?, ?, ?)",
        vt_rows,
    )
    con.executemany(
        "INSERT INTO commentary (verse_id, commentator_id, lang, text) VALUES (?, ?, ?, ?)",
        commentary_rows,
    )

    # --- FTS (external content: no text duplication) ---
    con.execute("INSERT INTO commentary_fts(commentary_fts) VALUES('rebuild')")
    con.execute("INSERT INTO verse_fts(verse_fts) VALUES('rebuild')")

    con.execute("PRAGMA user_version = 2")  # Room expects a non-zero version on a prepackaged DB
    con.commit()
    con.execute("VACUUM")
    con.commit()
    return con, slok_files, chapter_files


def verify(con, slok_files, chapter_files):
    """Full round-trip: rebuild every source JSON from the DB and diff it."""
    ok = True
    q = con.execute

    counts = {
        t: q(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        for t in ("commentator", "chapter", "chapter_translation", "verse",
                  "verse_translation", "commentary")
    }
    print("row counts:", counts)
    expected = {
        "commentator": 22, "chapter": 18, "chapter_translation": 72,
        "verse": 719, "verse_translation": 2876, "commentary": 72600,
    }
    if counts != expected:
        print("  FAIL expected", expected)
        ok = False

    # chapters round-trip (source key order: meaning/summary hi,en,be,ka per file)
    for path in chapter_files:
        src = json.load(open(path, encoding="utf-8"))
        ch = src["chapter_number"]
        r = q("""SELECT verses_count, name_sa, translation, transliteration
                 FROM chapter WHERE chapter_number=?""", (ch,)).fetchone()
        tr = dict_by_lang(q("SELECT lang, meaning, summary FROM chapter_translation WHERE chapter=?", (ch,)))
        src_langs = list(src["meaning"].keys())
        got = {
            "chapter_number": ch, "verses_count": r[0], "name": r[1],
            "translation": r[2], "transliteration": r[3],
            "meaning": {l: tr[l][0] for l in src_langs},
            "summary": {l: tr[l][1] for l in src_langs},
        }
        if got != src:
            print("  FAIL chapter round-trip:", path)
            ok = False

    # verses round-trip (author diffs tracked separately — normalised on purpose)
    author_normalised = 0
    authors = dict(q("SELECT id, author_name FROM commentator").fetchall())
    for path in slok_files:
        src = json.load(open(path, encoding="utf-8"))
        vid = verse_pk(src["chapter"], src["verse"])
        r = q("SELECT ext_id, chapter, verse_number, transliteration FROM verse WHERE id=?", (vid,)).fetchone()
        vt = dict_by_lang(q("SELECT lang, speaker, slok FROM verse_translation WHERE verse_id=?", (vid,)))
        got = {
            "_id": r[0], "chapter": r[1], "verse": r[2],
            "speaker": {l: vt[l][0] for l in src["speaker"]},
            "slok": {l: vt[l][1] for l in src["slok"]},
            "transliteration": r[3],
        }
        cm = {}
        for cid, lang, text in q(
            "SELECT commentator_id, lang, text FROM commentary WHERE verse_id=?", (vid,)
        ).fetchall():
            cm.setdefault(cid, {})[lang] = text
        for cid in COMMENTATOR_IDS:
            got[cid] = {"commentary": {l: cm[cid][l] for l in LANGS if l in cm[cid]}}
            src_block = dict(src[cid])
            if src_block.pop("author", None) != authors[cid]:
                author_normalised += 1
            if {"commentary": src_block["commentary"]} != got[cid]:
                print("  FAIL commentary round-trip:", path, cid)
                ok = False
            del got[cid]
        stripped_src = {k: v for k, v in src.items() if k not in COMMENTATOR_IDS}
        if got != stripped_src:
            print("  FAIL verse round-trip:", path)
            ok = False

    print(f"round-trip: {len(chapter_files)} chapters + {len(slok_files)} verses compared")
    print(f"author fields normalised (expected, not data loss): {author_normalised}")

    # FTS smoke queries
    n = q("SELECT COUNT(*) FROM commentary_fts WHERE commentary_fts MATCH 'Kurukshetra'").fetchone()[0]
    print(f"FTS commentary MATCH 'Kurukshetra': {n} hits")
    if n == 0:
        ok = False
    n = q("SELECT COUNT(*) FROM verse_fts WHERE verse_fts MATCH 'dharmakṣetre'").fetchone()[0]
    print(f"FTS verse MATCH 'dharmakṣetre': {n} hits")

    # language-pack query smoke test: rows a Hindi-only install would download/keep
    pack = {
        "chapter_translation": q("SELECT COUNT(*) FROM chapter_translation WHERE lang='hi'").fetchone()[0],
        "verse_translation": q("SELECT COUNT(*) FROM verse_translation WHERE lang='hi'").fetchone()[0],
        "commentary": q("SELECT COUNT(*) FROM commentary WHERE lang='hi'").fetchone()[0],
    }
    print("hi language-pack rows:", pack)

    # joined-query smoke test (the app's main read path)
    row = q(
        """SELECT v.ext_id, c.author_name, cm.text
           FROM verse v
           JOIN commentary cm ON cm.verse_id = v.id
           JOIN commentator c ON c.id = cm.commentator_id
           WHERE v.chapter=1 AND v.verse_number=1 AND cm.lang='en' AND cm.commentator_id='tej'"""
    ).fetchone()
    print("sample read:", row[0], "|", row[1], "|", row[2][:60] + "...")

    print(f"db size: {os.path.getsize(DB_PATH) / 1024 / 1024:.1f} MB")
    return ok


def dict_by_lang(cursor):
    return {row[0]: row[1:] for row in cursor.fetchall()}


if __name__ == "__main__":
    con, slok_files, chapter_files = build()
    print("built", DB_PATH)
    ok = verify(con, slok_files, chapter_files)
    con.close()
    print("OK" if ok else "FAILED")
    sys.exit(0 if ok else 1)
