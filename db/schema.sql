-- Bhagavad Gita — normalized schema (SQLite / Room-compatible)
-- Language is data, never a column. Adding a new language = INSERT rows, no migration.
-- Image columns hold paths only; base = https://neilsayok.github.io/gita-images/

CREATE TABLE language (
    code            TEXT NOT NULL PRIMARY KEY,   -- 'hi','en','be','ka','sa'
    name_native     TEXT NOT NULL,
    name_en         TEXT NOT NULL,
    is_script_only  INTEGER NOT NULL DEFAULT 0   -- 1 = 'sa': source text, never a translation target
);

CREATE TABLE chapter (
    chapter_number  INTEGER NOT NULL PRIMARY KEY,
    verses_count    INTEGER NOT NULL,
    name_sanskrit   TEXT NOT NULL,               -- chapter.name (Devanagari)
    translation     TEXT NOT NULL,               -- 'Arjuna Visada Yoga'
    transliteration TEXT NOT NULL,               -- 'Arjun Viṣhād Yog'
    img_landscape   TEXT NOT NULL,               -- 'chapters/chapter_1/landscape/img.jpeg'
    img_portrait    TEXT NOT NULL,
    img_square      TEXT NOT NULL
);

CREATE TABLE chapter_translation (
    chapter_number  INTEGER NOT NULL REFERENCES chapter(chapter_number) ON DELETE CASCADE,
    lang_code       TEXT NOT NULL REFERENCES language(code) ON DELETE CASCADE,
    meaning         TEXT,
    summary         TEXT,
    PRIMARY KEY (chapter_number, lang_code)
);
CREATE INDEX idx_chapter_translation_lang ON chapter_translation(lang_code);

CREATE TABLE verse (
    verse_id        TEXT NOT NULL PRIMARY KEY,   -- '_id', e.g. 'BG1.1'
    chapter_number  INTEGER NOT NULL REFERENCES chapter(chapter_number) ON DELETE CASCADE,
    verse_number    INTEGER NOT NULL,
    transliteration TEXT NOT NULL,               -- legacy top-level field, == verse_text.en.slok
    img_landscape   TEXT NOT NULL,               -- 'sloks/chapter_1/slok_1/landscape/img.jpeg'
    img_portrait    TEXT NOT NULL,
    img_square      TEXT NOT NULL
);
CREATE UNIQUE INDEX idx_verse_ch_no ON verse(chapter_number, verse_number);

-- Same Sanskrit verse rendered per script. NOT a meaning translation.
CREATE TABLE verse_text (
    verse_id        TEXT NOT NULL REFERENCES verse(verse_id) ON DELETE CASCADE,
    lang_code       TEXT NOT NULL REFERENCES language(code) ON DELETE CASCADE,
    speaker         TEXT,
    slok            TEXT,
    PRIMARY KEY (verse_id, lang_code)
);
CREATE INDEX idx_verse_text_lang ON verse_text(lang_code);

-- Meaning-level per-verse prose (currently only life_application, en).
CREATE TABLE verse_translation (
    verse_id         TEXT NOT NULL REFERENCES verse(verse_id) ON DELETE CASCADE,
    lang_code        TEXT NOT NULL REFERENCES language(code) ON DELETE CASCADE,
    life_application TEXT,
    PRIMARY KEY (verse_id, lang_code)
);
CREATE INDEX idx_verse_translation_lang ON verse_translation(lang_code);

CREATE TABLE theme (
    theme_id   INTEGER NOT NULL PRIMARY KEY,
    slug       TEXT NOT NULL UNIQUE             -- 'self_realization'
);
CREATE TABLE theme_translation (
    theme_id   INTEGER NOT NULL REFERENCES theme(theme_id) ON DELETE CASCADE,
    lang_code  TEXT NOT NULL REFERENCES language(code) ON DELETE CASCADE,
    name       TEXT NOT NULL,                   -- 'Self-Realization'
    PRIMARY KEY (theme_id, lang_code)
);
CREATE INDEX idx_theme_translation_lang ON theme_translation(lang_code);

CREATE TABLE verse_theme (
    verse_id   TEXT NOT NULL REFERENCES verse(verse_id) ON DELETE CASCADE,
    theme_id   INTEGER NOT NULL REFERENCES theme(theme_id) ON DELETE CASCADE,
    position   INTEGER NOT NULL,                -- preserves JSON array order
    PRIMARY KEY (verse_id, theme_id)
);
CREATE INDEX idx_verse_theme_theme ON verse_theme(theme_id);

CREATE TABLE word_meaning (
    verse_id        TEXT NOT NULL REFERENCES verse(verse_id) ON DELETE CASCADE,
    position        INTEGER NOT NULL,           -- word order within the verse
    sanskrit        TEXT NOT NULL,
    transliteration TEXT NOT NULL,
    PRIMARY KEY (verse_id, position)
);

CREATE TABLE word_meaning_translation (
    verse_id   TEXT NOT NULL,
    position   INTEGER NOT NULL,
    lang_code  TEXT NOT NULL REFERENCES language(code) ON DELETE CASCADE,
    meaning    TEXT NOT NULL,
    PRIMARY KEY (verse_id, position, lang_code),
    FOREIGN KEY (verse_id, position) REFERENCES word_meaning(verse_id, position) ON DELETE CASCADE
);
CREATE INDEX idx_wmt_lang ON word_meaning_translation(lang_code);

CREATE TABLE commentator (
    commentator_key TEXT NOT NULL PRIMARY KEY,  -- 'tej','siva',...,'prabhu'
    author          TEXT NOT NULL,              -- canonical; fixes 45 blocks missing "author"
    display_order   INTEGER NOT NULL
);

CREATE TABLE commentary (
    verse_id        TEXT NOT NULL REFERENCES verse(verse_id) ON DELETE CASCADE,
    commentator_key TEXT NOT NULL REFERENCES commentator(commentator_key) ON DELETE CASCADE,
    lang_code       TEXT NOT NULL REFERENCES language(code) ON DELETE CASCADE,
    text            TEXT,
    PRIMARY KEY (verse_id, commentator_key, lang_code)
);
CREATE INDEX idx_commentary_commentator ON commentary(commentator_key);
CREATE INDEX idx_commentary_lang ON commentary(lang_code);
