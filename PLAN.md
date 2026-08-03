# Room DB Schema for Gita Compose Multiplatform App

## Context

The repo holds a fully translated Bhagavad Gita dataset: 18 chapter JSON files and 719 slok JSON files (one per verse). User is building a Compose Multiplatform app and wants this data in a Room database, shipped prepopulated, with FTS search. Requirement: **lossless** conversion.

Data survey results (all 719 slok files verified):
- Uniform structure: `_id, chapter, verse, speaker{hi,be,en,ka}, slok{hi,be,en,ka}, transliteration` + 22 commentator blocks.
- Every commentator block: `{author, commentary{hi,en,be,ka[,sa]}}`. `sa` present on 9,328 of 15,818 blocks. Zero empty strings, zero non-string values. 72,600 text fields total.
- Anomalies to normalize during seeding: `slok/bhagavadgita_chapter_6_slok_48.json` and `..._7_slok_31.json` have blocks missing `author`; `prabhu` author appears as both "Swami Prabhupada" and "A.C. Bhaktivedanta Swami Prabhupada". Fixed by a canonical commentator lookup table — no data loss, author lives there anyway.
- Chapter files uniform: `chapter_number, verses_count, name, translation, transliteration, meaning{en,hi}, summary{en,hi}`.

## Schema decision: row-per-language for commentary

Chosen after inspecting the data (user asked for data-driven decision):
- Commentary is the bulk (72,600 texts). Row-per-language means a "show verse in Bengali" query loads only Bengali rows, not 5-language rows with 4 unused columns.
- `sa` optionality is naturally lossless: a `sa` row exists only where the JSON had one. Column-per-language would need NULL-vs-absent convention.
- `speaker`/`slok` are always exactly 4 fixed languages and tiny — columns there, no reason for rows.

## DB Schema

```sql
-- Static lookup: 22 rows. Fixes the author anomalies at the source.
CREATE TABLE commentator (
    id          TEXT NOT NULL PRIMARY KEY,   -- json key: 'tej', 'siva', ...
    author_name TEXT NOT NULL                -- canonical: 'Swami Tejomayananda', ...
);

CREATE TABLE chapter (
    chapter_number  INTEGER NOT NULL PRIMARY KEY,
    verses_count    INTEGER NOT NULL,
    name_sa         TEXT NOT NULL,           -- 'अर्जुनविषादयोग'
    translation     TEXT NOT NULL,           -- 'Arjuna Visada Yoga'
    transliteration TEXT NOT NULL,           -- 'Arjun Viṣhād Yog'
    meaning_en      TEXT NOT NULL,
    meaning_hi      TEXT NOT NULL,
    summary_en      TEXT NOT NULL,
    summary_hi      TEXT NOT NULL
);

CREATE TABLE verse (
    id              TEXT NOT NULL PRIMARY KEY,  -- original _id, e.g. 'BG1.1'
    chapter         INTEGER NOT NULL REFERENCES chapter(chapter_number),
    verse           INTEGER NOT NULL,
    speaker_hi      TEXT NOT NULL,
    speaker_en      TEXT NOT NULL,
    speaker_be      TEXT NOT NULL,
    speaker_ka      TEXT NOT NULL,
    slok_hi         TEXT NOT NULL,           -- Devanagari
    slok_en         TEXT NOT NULL,           -- IAST
    slok_be         TEXT NOT NULL,           -- Bengali script
    slok_ka         TEXT NOT NULL,           -- Kannada script
    transliteration TEXT NOT NULL,           -- legacy field, kept (lossless)
    UNIQUE(chapter, verse)
);
CREATE INDEX idx_verse_chapter ON verse(chapter);

CREATE TABLE commentary (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    verse_id       TEXT NOT NULL REFERENCES verse(id),
    commentator_id TEXT NOT NULL REFERENCES commentator(id),
    lang           TEXT NOT NULL,            -- 'hi'|'en'|'be'|'ka'|'sa'
    text           TEXT NOT NULL,
    UNIQUE(verse_id, commentator_id, lang)
);
CREATE INDEX idx_commentary_verse_lang ON commentary(verse_id, lang);

-- FTS4 (Room @Fts4, works across KMP targets) over verse text + commentary.
-- contentEntity = commentary for commentary search; separate small FTS table for slok text.
CREATE VIRTUAL TABLE commentary_fts USING fts4(text, content=`commentary`);
CREATE VIRTUAL TABLE verse_fts USING fts4(slok_hi, slok_en, slok_be, slok_ka, content=`verse`);
```

Lossless check: every JSON field maps to a column/row — `_id`→verse.id, `transliteration` kept, `sa` presence preserved by row existence, `author` normalized into `commentator` (the two authorless files and prabhu variant carry no extra info). Reversible back to JSON.

## Room (KMP) entity sketch

- `@Entity Commentator`, `@Entity Chapter`, `@Entity Verse`, `@Entity Commentary` mirroring above; `@Fts4(contentEntity = Commentary::class) CommentaryFts`, same for `VerseFts`.
- Room KMP (androidx.room 2.7+) with `BundledSQLiteDriver`; prepopulate via `createFromAsset` on Android / copy-db-from-resources on iOS/desktop before open.

## Schema v2 (current) — languages as rows, image provisions, language packs

Supersedes the sketch above; canonical DDL is `schema.sql`. Changes driven by three new
requirements: chapter meaning/summary now exist in 4 languages, more languages will be added
later, and the app will download only Sanskrit (default) + the user's chosen language.

- **All per-language text is row-per-language** — `chapter_translation(chapter, lang, meaning,
  summary)`, `verse_translation(verse_id, lang, speaker, slok)`, and `commentary` (unchanged).
  Adding a language = inserting rows, never `ALTER TABLE`.
- **Language pack = `WHERE lang='X'`** across those three tables. Base DB carries the
  language-independent core (chapter/verse structure, canonical Sanskrit/IAST fields,
  commentator lookup) plus `sa` commentary rows. Hindi pack measured: 18 + 719 + 15,818 rows.
- **Image provisions (all nullable TEXT, no data yet):** `chapter.image_square/landscape/portrait`,
  `verse.image_square/landscape/portrait`, `commentator.image`.
- `verse_fts` now indexes `verse_translation.slok` (external content); `commentary_fts` unchanged.
- `PRAGMA user_version = 2`.

v2 verification (same full round-trip as v1, all passing): 22 commentators, 18 chapters,
72 chapter_translation, 719 verses, 2,876 verse_translation, 72,600 commentary rows; all 737
source files reconstructed byte-equal (61 author normalisations expected); FTS hits present;
120.6 MB.

## Schema deviations made during implementation (for Room compatibility)

The canonical DDL is `schema.sql`; it differs from the sketch above in three ways:

1. **`verse.id` is an INTEGER rowid alias** (`chapter * 1000 + verse_number`) instead of the
   string `_id`. External-content FTS links to its content table by rowid, and Room's
   `@Fts4(contentEntity = ...)` requires the same. The original string `_id` is preserved
   verbatim in `verse.ext_id` (unique), so nothing is lost. `commentary.verse_id` is INTEGER.
2. **Uniqueness is expressed as explicit `CREATE UNIQUE INDEX`**, not inline `UNIQUE(...)`
   constraints. Room validates a prepackaged DB's *indices*; an inline table constraint creates
   an invisible `sqlite_autoindex_*` that Room cannot match, which fails schema validation.
   Index names follow Room's default `index_<table>_<cols>` convention.
3. **`commentator.sort_order`** added, preserving the commentator ordering used in the JSON
   files (otherwise the app cannot reproduce the original display order).

`PRAGMA user_version = 1` is set — Room rejects a prepackaged DB left at version 0.
`room_master_table` is deliberately *not* created: when it is absent, Room validates the real
schema against the entity definitions and then writes the identity hash itself.

## Build

`python3 build_db.py` — reads `chapter/` + `slok/`, applies `schema.sql`, inserts the canonical
22-commentator lookup, bulk-inserts verses and commentary, rebuilds both FTS indices, sets
`user_version`, and VACUUMs.

## Verification — done, passing

`python3 build_db.py` completes in ~2.5s and prints:

- Row counts exactly as predicted: 22 commentators, 18 chapters, 719 verses, **72,600 commentary rows**.
- **Full round-trip**, not a spot check: all 18 chapter files and all 719 slok files are
  reconstructed from the DB and compared against source. Zero differences.
- 61 `author` fields normalised — the only intentional divergence: 45 blocks that had no
  `author` key at all (`chapter_6_slok_48`, `chapter_7_slok_31`, plus `prabhu` in
  `chapter_8_slok_29`) and 16 `prabhu` blocks spelled "Swami Prabhupada" rather than
  "A.C. Bhaktivedanta Swami Prabhupada". Author lives in the `commentator` lookup, so no text lost.
- FTS smoke queries return hits (`commentary_fts MATCH 'Kurukshetra'` → 24;
  `verse_fts MATCH 'dharmakṣetre'` → 1). `PRAGMA integrity_check` → ok.

Output: **`gita.db`, 121 MB** (33.8 MB gzipped; APK/AAB compresses it, so shipped cost is
closer to the compressed figure). External-content FTS is what keeps this from being much
larger — the searchable text is not duplicated into the index.

## Remaining work (app repo, not here)

Room `@Entity`/`@Dao` declarations must match `schema.sql` exactly or Room will reject the
prepackaged DB at first open. Entity classes are not in this repo.
