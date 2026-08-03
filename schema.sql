-- Bhagavad Gita Room/SQLite schema v2 (see PLAN.md for rationale)
-- Built by build_db.py. Room-compatible: uniqueness is expressed as explicit
-- indices (Room validates indices, not inline UNIQUE constraints) and index
-- names follow Room's default `index_<table>_<cols>` convention.
--
-- v2 design: ALL per-language text lives in row-per-language tables
-- (chapter_translation, verse_translation, commentary). Adding a language later
-- = inserting rows, never ALTER TABLE. This is also the download unit: the base
-- DB ships language-independent structure + Sanskrit sources; a language pack
-- for lang X = every row WHERE lang='X' across the three translation tables.
-- Image columns are nullable provisions — no image data exists yet.

-- Static lookup: 22 rows. Canonical author names (fixes missing/variant authors
-- in the source JSON). sort_order preserves the commentator order used in the JSON.
CREATE TABLE commentator (
    id          TEXT NOT NULL PRIMARY KEY,   -- json key: 'tej', 'siva', ...
    author_name TEXT NOT NULL,               -- canonical: 'Swami Tejomayananda', ...
    sort_order  INTEGER NOT NULL,            -- display order, 0..21
    image       TEXT                         -- translator portrait (URL/asset path), null until added
);

-- Language-independent chapter core. name_sa/translation/transliteration are
-- canonical (Sanskrit/IAST), not per-language text.
CREATE TABLE chapter (
    chapter_number  INTEGER NOT NULL PRIMARY KEY,
    verses_count    INTEGER NOT NULL,
    name_sa         TEXT NOT NULL,           -- 'अर्जुनविषादयोग'
    translation     TEXT NOT NULL,           -- 'Arjuna Visada Yoga'
    transliteration TEXT NOT NULL,           -- 'Arjun Viṣhād Yog'
    image_square    TEXT,                    -- null until image assets exist
    image_landscape TEXT,
    image_portrait  TEXT
);

-- Per-language chapter text. One row per (chapter, lang).
CREATE TABLE chapter_translation (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter  INTEGER NOT NULL REFERENCES chapter(chapter_number),
    lang     TEXT NOT NULL,                  -- 'hi'|'en'|'be'|'ka'|future
    meaning  TEXT NOT NULL,
    summary  TEXT NOT NULL
);
CREATE UNIQUE INDEX index_chapter_translation_chapter_lang ON chapter_translation(chapter, lang);
CREATE INDEX index_chapter_translation_lang ON chapter_translation(lang);

-- Language-independent verse core. id is an INTEGER rowid alias
-- (chapter*1000 + verse_number); original string `_id` preserved in ext_id.
CREATE TABLE verse (
    id              INTEGER NOT NULL PRIMARY KEY,
    ext_id          TEXT NOT NULL,           -- original _id, e.g. 'BG1.1'
    chapter         INTEGER NOT NULL REFERENCES chapter(chapter_number),
    verse_number    INTEGER NOT NULL,
    transliteration TEXT NOT NULL,           -- IAST romanization of the Sanskrit verse
    image_square    TEXT,                    -- null until image assets exist
    image_landscape TEXT,
    image_portrait  TEXT
);
CREATE INDEX idx_verse_chapter ON verse(chapter);
CREATE UNIQUE INDEX index_verse_ext_id ON verse(ext_id);
CREATE UNIQUE INDEX index_verse_chapter_verse_number ON verse(chapter, verse_number);

-- Per-language verse rendering: the Sanskrit shloka in that language's script
-- (en = IAST) and the speaker's name in that script. One row per (verse, lang).
CREATE TABLE verse_translation (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    verse_id INTEGER NOT NULL REFERENCES verse(id),
    lang     TEXT NOT NULL,                  -- 'hi'|'en'|'be'|'ka'|future
    speaker  TEXT NOT NULL,                  -- e.g. 'धृतराष्ट्र' / 'Dhritarashtra'
    slok     TEXT NOT NULL                   -- the verse text in this script
);
CREATE UNIQUE INDEX index_verse_translation_verse_id_lang ON verse_translation(verse_id, lang);
CREATE INDEX index_verse_translation_lang ON verse_translation(lang);

-- Per-language commentary. 'sa' rows are the Sanskrit source (ships in the base
-- DB, present only where the commentator wrote Sanskrit); other langs are packs.
CREATE TABLE commentary (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    verse_id       INTEGER NOT NULL REFERENCES verse(id),
    commentator_id TEXT NOT NULL REFERENCES commentator(id),
    lang           TEXT NOT NULL,            -- 'hi'|'en'|'be'|'ka'|'sa'|future
    text           TEXT NOT NULL
);
CREATE INDEX index_commentary_verse_id_lang ON commentary(verse_id, lang);
CREATE INDEX index_commentary_commentator_id ON commentary(commentator_id);
CREATE UNIQUE INDEX index_commentary_verse_id_commentator_id_lang
    ON commentary(verse_id, commentator_id, lang);

-- FTS4 external-content tables (Room @Fts4(contentEntity = ...)): text is not
-- duplicated; the index points back at the content table by rowid.
CREATE VIRTUAL TABLE commentary_fts USING fts4(text, content=`commentary`);
CREATE VIRTUAL TABLE verse_fts USING fts4(slok, content=`verse_translation`);
