#!/usr/bin/env python3
"""Build a normalized, lossless SQLite database from the Bhagavad Gita JSON corpus.

Reads chapter/*.json and slok/*.json and populates a fully-normalized schema
(plain text only, no JSON blobs), VACUUMs the result for a tight read-only
asset, then emits two files:

    gita.db       - the runtime SQLite database (open this with SQLDelight/Room)
    gita.db.gz    - gzip-compressed copy to ship inside the app and gunzip on
                    first launch (Okio GzipSource works on every CMP target)

Losslessness is enforced: every top-level slok key is either a known scalar
field or a commentator object (a dict containing an "author" key). Anything
unexpected aborts the build with a clear message so the schema can be extended
rather than silently dropping data. Author/field ordering is preserved via the
`ordinal` column.

Usage:
    python3 TOOLS/build_db.py                 # builds into the repo root
    python3 TOOLS/build_db.py --root /path    # override corpus/output root
"""
import argparse
import gzip
import json
import sqlite3
import sys
from pathlib import Path

# Top-level slok keys that are plain fields, not commentator objects.
SLOK_SCALAR_KEYS = {"_id", "chapter", "verse", "speaker", "slok", "transliteration"}

# Recognized sub-keys inside chapter meaning/summary objects.
CHAPTER_LANG_KEYS = {"en", "hi"}
CHAPTER_SCALAR_KEYS = {
    "chapter_number", "verses_count", "name", "translation", "transliteration",
}

SCHEMA = """
CREATE TABLE chapters (
    chapter_number  INTEGER PRIMARY KEY,
    name            TEXT,
    translation     TEXT,
    transliteration TEXT,
    meaning_en      TEXT,
    meaning_hi      TEXT,
    summary_en      TEXT,
    summary_hi      TEXT,
    verses_count    INTEGER
);

CREATE TABLE speakers (
    speaker_id INTEGER PRIMARY KEY,
    name       TEXT UNIQUE
);

CREATE TABLE authors (
    author_code TEXT PRIMARY KEY,
    name        TEXT
);

CREATE TABLE sloks (
    id              TEXT PRIMARY KEY,
    chapter_number  INTEGER REFERENCES chapters(chapter_number),
    verse           INTEGER,
    speaker_id      INTEGER REFERENCES speakers(speaker_id),
    slok_text       TEXT,
    transliteration TEXT,
    image_url       TEXT
);

CREATE TABLE translations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    slok_id     TEXT REFERENCES sloks(id),
    author_code TEXT REFERENCES authors(author_code),
    field_type  TEXT,
    ordinal     INTEGER,
    text        TEXT,
    UNIQUE(slok_id, author_code, field_type)
);
"""


def die(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def load_json(path):
    try:
        with path.open(encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as exc:
        die(f"{path}: invalid JSON - {exc}")


def build_chapters(conn, chapter_dir):
    files = sorted(chapter_dir.glob("*.json"))
    if not files:
        die(f"no chapter files found in {chapter_dir}")
    rows = []
    for path in files:
        c = load_json(path)
        extra = set(c) - CHAPTER_SCALAR_KEYS - {"meaning", "summary"}
        if extra:
            die(f"{path}: unexpected chapter keys {sorted(extra)} - extend the schema")
        meaning = c.get("meaning", {}) or {}
        summary = c.get("summary", {}) or {}
        for label, obj in (("meaning", meaning), ("summary", summary)):
            extra_lang = set(obj) - CHAPTER_LANG_KEYS
            if extra_lang:
                die(f"{path}: unexpected {label} languages {sorted(extra_lang)} - extend the schema")
        rows.append((
            c["chapter_number"], c.get("name"), c.get("translation"),
            c.get("transliteration"), meaning.get("en"), meaning.get("hi"),
            summary.get("en"), summary.get("hi"), c.get("verses_count"),
        ))
    rows.sort(key=lambda r: r[0])
    conn.executemany(
        "INSERT INTO chapters VALUES (?,?,?,?,?,?,?,?,?)", rows
    )
    return len(rows)


def build_sloks(conn, slok_dir):
    files = sorted(slok_dir.glob("*.json"))
    if not files:
        die(f"no slok files found in {slok_dir}")

    sloks = [load_json(p) for p in files]
    # Deterministic order by (chapter, verse).
    sloks.sort(key=lambda s: (s.get("chapter", 0), s.get("verse", 0)))

    speakers = {}        # name -> speaker_id
    authors = {}         # code -> name
    slok_rows = []
    translation_rows = []

    for s in sloks:
        # Validate: every top-level key is a known scalar or a commentator object.
        commentator_codes = []
        for key, val in s.items():
            if key in SLOK_SCALAR_KEYS:
                continue
            if isinstance(val, dict) and "author" in val:
                commentator_codes.append(key)
                continue
            die(f"slok {s.get('_id')}: unexpected top-level key {key!r} "
                f"(value type {type(val).__name__}) - extend the schema")

        speaker_name = s.get("speaker")
        speaker_id = None
        if speaker_name is not None:
            speaker_id = speakers.setdefault(speaker_name, len(speakers) + 1)

        slok_rows.append((
            s["_id"], s.get("chapter"), s.get("verse"), speaker_id,
            s.get("slok"), s.get("transliteration"), None,  # image_url: populate later
        ))

        # Preserve original author + field order via a running ordinal.
        ordinal = 0
        for code in commentator_codes:
            block = s[code]
            name = block.get("author")
            if code in authors and authors[code] != name and name is not None:
                print(f"  warning: author code {code!r} has differing names "
                      f"({authors[code]!r} vs {name!r}); keeping first", file=sys.stderr)
            authors.setdefault(code, name)
            for field_type, text in block.items():
                if field_type == "author":
                    continue
                translation_rows.append((
                    s["_id"], code, field_type, ordinal, text,
                ))
                ordinal += 1

    conn.executemany(
        "INSERT INTO speakers (speaker_id, name) VALUES (?,?)",
        [(sid, name) for name, sid in sorted(speakers.items(), key=lambda kv: kv[1])],
    )
    conn.executemany(
        "INSERT INTO authors (author_code, name) VALUES (?,?)",
        sorted(authors.items()),
    )
    conn.executemany(
        "INSERT INTO sloks (id, chapter_number, verse, speaker_id, slok_text, "
        "transliteration, image_url) VALUES (?,?,?,?,?,?,?)",
        slok_rows,
    )
    conn.executemany(
        "INSERT INTO translations (slok_id, author_code, field_type, ordinal, text) "
        "VALUES (?,?,?,?,?)",
        translation_rows,
    )
    return len(slok_rows), len(speakers), len(authors), len(translation_rows)


def gzip_file(src, dst):
    # mtime=0 keeps the output byte-stable across rebuilds.
    data = src.read_bytes()
    with gzip.GzipFile(filename="", mode="wb", fileobj=dst.open("wb"), mtime=0) as gz:
        gz.write(data)


def human(n):
    for unit in ("B", "KB", "MB"):
        if n < 1024 or unit == "MB":
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} B"
        n /= 1024


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    default_root = Path(__file__).resolve().parent.parent
    parser.add_argument("--root", type=Path, default=default_root,
                        help="repo root containing chapter/ and slok/ (default: parent of TOOLS/)")
    parser.add_argument("--out", type=Path, default=None,
                        help="output .db path (default: <root>/gita.db)")
    args = parser.parse_args()

    root = args.root.resolve()
    chapter_dir = root / "chapter"
    slok_dir = root / "slok"
    db_path = (args.out or root / "gita.db").resolve()
    gz_path = db_path.with_suffix(db_path.suffix + ".gz")

    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA)
        n_ch = build_chapters(conn, chapter_dir)
        n_sl, n_sp, n_au, n_tr = build_sloks(conn, slok_dir)
        conn.commit()
        conn.execute("VACUUM")
        conn.commit()
    finally:
        conn.close()

    gzip_file(db_path, gz_path)

    db_size = db_path.stat().st_size
    gz_size = gz_path.stat().st_size
    print("Build complete.")
    print(f"  chapters     : {n_ch}")
    print(f"  speakers     : {n_sp}")
    print(f"  authors      : {n_au}")
    print(f"  sloks        : {n_sl}")
    print(f"  translations : {n_tr}")
    print()
    print(f"  {db_path.name:14}: {human(db_size)}  (runtime DB)")
    print(f"  {gz_path.name:14}: {human(gz_size)}  (ship this, gunzip on first launch)")
    print(f"  compression  : {db_size / gz_size:.1f}x smaller")


if __name__ == "__main__":
    main()
