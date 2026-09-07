# Import prebuilt Bhagavad Gita SQLite DB into this Compose Multiplatform project

I have a prebuilt, normalized SQLite database (`gita.db`, ~99 MB) for a Bhagavad Gita app,
built outside this project. I need it wired into this Compose Multiplatform (KMP) codebase
as a **bundled, read-only, shared-source-set database** — same queries on Android, iOS,
and Desktop.

## Import From Location 
/Users/neil/AndroidStudioProjects/Gita/V1/DB/bhagavad-gita/db

## Files I'm providing

- `gita.db` — the finished SQLite file, all data already loaded.
- `schema.sql` — authoritative DDL (paste below). Do not re-derive the schema from the
  binary; use this file as source of truth for types, keys, and comments explaining
  non-obvious columns.

## Schema shape — read this before writing any query

Language is a **row**, never a column. Every translatable table has a matching
`_translation`/`_text` table keyed by `(<entity_id>, lang_code)`. `language.code` values:
`hi`, `en`, `be`, `ka`, `sa` (`sa` = Sanskrit script only, `is_script_only=1`, never a
translation target — don't offer it as a UI language).

A **missing row** in a translation table means "not translated yet for that language",
not an error — always fall back to `en` when a lookup misses, never assume every
`(entity, lang)` pair exists.

Key tables:
- `chapter` (18 rows) + `chapter_translation` (meaning/summary per lang)
- `verse` (719 rows, PK `verse_id` e.g. `"BG1.1"`) + `verse_text` (speaker/slok per
  script — this is the Sanskrit rendered in different scripts, NOT a meaning translation)
  + `verse_translation` (life_application prose, currently `en` only)
- `theme` / `theme_translation` / `verse_theme` (join table, `position` preserves order)
- `word_meaning` (sanskrit + transliteration, language-neutral) / `word_meaning_translation`
  (per-word gloss per lang)
- `commentator` (22 rows, canonical author names) / `commentary` (72,600 rows, keyed
  `(verse_id, commentator_key, lang_code)`)

Image columns (`img_landscape`, `img_portrait`, `img_square`) on `chapter` and `verse`
hold **relative paths only**, e.g. `"chapters/chapter_12/portrait/img.jpeg"` or
`"sloks/chapter_5/slok_4/landscape/img.jpeg"`. Prepend this base URL at read time (do not
hardcode it into the DB):

```
https://neilsayok.github.io/gita-images/
```

Every string cell is trimmed/non-empty when present — no need to defensively `.trim()`
values pulled from this DB.

## What I need you to do

1. **Pick and wire up a KMP-compatible SQLite layer** that can open a bundled, prepopulated
   `.db` file read-only from `commonMain` and expose `suspend`/`Flow` query functions
   callable from shared Compose UI code. Use whichever this project already depends on if
   one is present (SQLDelight or Room 2.7+ KMP) — check `libs.versions.toml` /
   `build.gradle.kts` first. If neither is present, default to **Room 2.7+ with KMP
   support** (`androidx.room:room-runtime` + `androidx.sqlite:sqlite-bundled`), since Room
   entity classes already matching this exact schema exist at `db/room/GitaEntities.kt` in
   the source repo — reuse/adapt those instead of hand-rolling new ones. Ask me to paste
   that file's contents if you need to see it.

2. **Bundle `gita.db` as a static asset**, then copy it to a writable path and open it
   there on first launch (KMP has no Android-only `createFromAsset` shortcut — you must
   copy-then-open on every target):
   - Android: place in `composeApp/src/androidMain/assets/gita.db`, copy from
     `context.assets` to `context.getDatabasePath("gita.db")` if absent.
   - iOS: place in `composeApp/src/iosMain/resources/gita.db` (or via `NSBundle`), copy to
     the app's `Documents`/`Library` directory if absent.
   - Desktop (JVM): place in `composeApp/src/jvmMain/resources/gita.db` on the classpath,
     copy to a user-data directory (e.g. `~/.gita/gita.db`) if absent.
   - Alternatively, if the chosen library supports it cleanly in KMP, use Compose
     Multiplatform resources (`composeResources`) as the single common location and copy
     out per-platform from there — pick whichever keeps the copy-on-first-launch logic in
     `commonMain` rather than duplicated per platform.
   - The DB is **read-only reference data** — no migrations needed for existing content;
     only add `Room`/SQLDelight schema versioning if you expect to ship DB updates later by
     replacing the whole asset file (bump a version marker, re-copy on mismatch).

3. **Write typed queries/DAOs** (or `.sq` files if SQLDelight) for at least:
   - Get all chapters with `chapter_translation` joined for a given `lang_code`
     (fallback to `en` per row if the requested language is missing).
   - Get all verses in a chapter, ordered by `verse_number`, with `verse_text` for the
     UI script and `verse_translation.life_application` for the UI language.
   - Get full detail for one verse: verse row + all `word_meaning`/`word_meaning_translation`
     (ordered by `position`) + all `commentary` for that verse joined to `commentator`
     (ordered by `commentator.display_order`), filtered to the requested `lang_code`.
   - Get themes for a verse (`verse_theme` joined to `theme_translation`, ordered by
     `position`).
   - A search across `verse_translation.life_application` and `commentary.text` for a
     given `lang_code` (simple `LIKE`; only add FTS if I ask for it).

4. **Expose a small repository interface** in `commonMain` (not raw DAOs) that Compose
   screens depend on, so UI code never sees SQL/Room/SQLDelight types directly — return
   plain data classes (e.g. `ChapterUi`, `VerseDetailUi`) with the image base URL already
   applied.

5. Tell me exactly which build files you touched and what Gradle sync steps I need to run
   afterward. Don't invent tables or columns beyond what's in the schema above — if
   something looks missing for a feature I mention later, ask rather than guessing new
   columns.

## Constraints

- Don't modify `gita.db` itself — it's generated from source JSON elsewhere; if a query
  need reveals a schema gap, tell me and I'll regenerate it upstream.
- Don't add a new database dependency if the project already has SQLDelight or Room wired
  up for something else — reuse it.
- Keep all SQL/DAO code multiplatform (`commonMain`); only the file-copy/bootstrap step
  should be `expect`/`actual` per platform.
