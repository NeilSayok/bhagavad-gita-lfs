# JSON → DB mapping

Source: `chapter/*.json` (18 files), `slok/*.json` (719 files).
Built by: `db/build_db.py` → `db/schema.sql` → `db/gita.db`.
Rule: language is a row, never a column — empty/whitespace string in JSON = no row inserted (a language "not translated yet" just has no row, not a NULL).

## language

Not derived from JSON — hardcoded list in `build_db.py`: `sa, hi, en, be, ka` (`is_script_only=1` for `sa` only).

## chapter/*.json → `chapter` (1 row per file) + `chapter_translation` (1 row per lang present)

| JSON field | Column | Table |
|---|---|---|
| `chapter_number` | `chapter_number` (PK) | `chapter` |
| `verses_count` | `verses_count` | `chapter` |
| `name` | `name_sanskrit` | `chapter` |
| `translation` | `translation` | `chapter` |
| `transliteration` | `transliteration` | `chapter` |
| — (generated) | `img_landscape/portrait/square` = `chapters/chapter_<n>/<variant>/img.jpeg` | `chapter` |
| `meaning.<lang>` | `meaning` | `chapter_translation` (PK `chapter_number, lang_code`), skipped if blank |
| `summary.<lang>` | `summary` | `chapter_translation`, skipped if blank |

A `chapter_translation` row is inserted per lang key present in either `meaning` or `summary`, only if at least one of the two is non-blank for that lang.

## slok/*.json → `verse` (1 row per file) + related tables

| JSON field | Column | Table |
|---|---|---|
| `_id` | `verse_id` (PK, e.g. `BG1.1`) | `verse` |
| `chapter` | `chapter_number` (FK → `chapter`) | `verse` |
| `verse` | `verse_number` | `verse` |
| `transliteration` (top-level, legacy) | `transliteration` | `verse` |
| — (generated) | `img_landscape/portrait/square` = `sloks/chapter_<c>/slok_<v>/<variant>/img.jpeg` | `verse` |

### `speaker.<lang>` + `slok.<lang>` → `verse_text` (PK `verse_id, lang_code`)

One row per lang key present in either `speaker` or `slok`, skipped if both blank for that lang.

| JSON field | Column |
|---|---|
| `speaker.<lang>` | `speaker` |
| `slok.<lang>` | `slok` |

### `life_application` → `verse_translation` (PK `verse_id, lang_code`)

Single row, hardcoded `lang_code = "en"` (source JSON only ever populates this field in English). Skipped entirely if blank.

| JSON field | Column |
|---|---|
| `life_application` | `life_application` |

### `themes[]` → `theme` / `theme_translation` / `verse_theme`

- `theme`/`theme_translation` are built once globally (first occurrence across all 719 files wins the `theme_id`; `slug` = slugified English name; `theme_translation.lang_code` is always `"en"` — themes have no other-language variant in source JSON).
- `verse_theme` gets one row per array element, `position` = array index (preserves JSON order).

| JSON field | Column | Table |
|---|---|---|
| `themes[i]` (name, dedup'd) | `theme_id` (assigned), `slug` | `theme` |
| `themes[i]` (name) | `name` (lang `en`) | `theme_translation` |
| index `i` | `position`; `theme_id` | `verse_theme` |

### `word_meanings[]` → `word_meaning` / `word_meaning_translation`

One row per array element, `position` = array index. PK is `(verse_id, position)`.

| JSON field | Column | Table |
|---|---|---|
| `word_meanings[i].sanskrit` | `sanskrit` | `word_meaning` |
| `word_meanings[i].transliteration` | `transliteration` | `word_meaning` |
| `word_meanings[i].meaning` | `meaning` (lang hardcoded `"en"`) | `word_meaning_translation`, skipped if blank |

### `<commentator_key>.author` → `commentator` (global, not per-verse)

For each of the 22 commentator keys (`tej, siva, purohit, chinmay, san, adi, gambir, madhav, anand, rams, raman, abhinav, sankar, jaya, vallabh, ms, srid, dhan, venkat, puru, neel, prabhu`), the **most frequent** non-blank `author` value across all 719 files is picked as the canonical `author` (fixes ~45 blocks with a missing/inconsistent author field). `display_order` = index in the fixed key list above.

### `<commentator_key>.commentary.<lang>` → `commentary` (PK `verse_id, commentator_key, lang_code`)

One row per (commentator key × lang) pair present in that block's `commentary` object, skipped if blank.

| JSON field | Column |
|---|---|
| `<key>.commentary.<lang>` | `text` |

## Fields NOT stored in the DB

- `speaker` transliteration duplication vs `slok` — both stored, no dedup.
- `sa` (Sanskrit) commentary text, when present, is stored like any other `lang_code` row in `commentary` — not treated specially beyond `language.is_script_only`.
- Source pre-restructure field names (`ht/hc/et/ec/sc`) are historical only — current JSON files already use the normalized `hi/en/be/ka/sa` keys; the DB builder never sees the old names.

## Integrity checks run by `build_db.py`'s `verify()`

- exactly 18 `chapter` rows, `n_sloks` `verse` rows, 22 `commentator` rows
- verse numbers contiguous `1..count` within every chapter
- zero foreign-key violations (`PRAGMA foreign_key_check`)
- at least 1 `commentary` row, spanning all 5 `lang_code` values

---

# DB → static API JSON mapping

The app is moving off `gita.db` entirely — every screen reads a **precomputed static JSON file** under `api/`, generated from `db/gita.db` by the scripts below. Nothing is computed on-device or on the fly. `api/meta/update.json` (built by `scripts/build_update_meta.py`) records a last-modified epoch per file under `api/`, so a client can cheaply detect which of these changed.

Devanagari note: `verse_text` has no `lang_code='sa'` rows in the DB (source JSON never populates a `sa` key for `speaker`/`slok`) — every API below sources Devanagari from **`lang_code='hi'`** instead, matching what the app's own pre-migration DAOs already did.

Default commentary note: "the" commentary for a verse (where a single value is needed, not the full per-commentator list) is always the row with the **lowest `commentator.display_order`** that has non-null `lang_code='en'` text — i.e. `tej` first, falling through the fixed `commentator` order.

## `api/reading/all.json` — reading screen

Script: `api/build_reading_api.py`. One array, one object per verse (719 total), all verses in one file.

| Field (nested) | Source | Notes |
|---|---|---|
| `chapter.translation` | `chapter.translation` | joined on `verse.chapter_number` |
| `verse.verse_id` | `verse.verse_id` | |
| `verse.chapter_number` | `verse.chapter_number` | |
| `verse.verse_number` | `verse.verse_number` | |
| `verse.transliteration` | `verse.transliteration` | |
| `verse.img_landscape` | `verse.img_landscape` | |
| `verse.img_square` | `verse.img_square` | |
| `verse_text.speaker` | `verse_text.speaker` | `lang_code='hi'` |
| `verse_text.slok` | `verse_text.slok` | `lang_code='hi'` |
| `verse_translation.life_application` | `verse_translation.life_application` | `lang_code='en'` |

## `api/chapter-slok/<chapter_number>/list.json` — chapter/reading-by-chapter screen

Script: `api/build_chapter_api.py`. One file per chapter (18 total), each `{ chapter: {translation}, sloks: [...] }` with one entry per verse in that chapter.

| Field (nested) | Source | Notes |
|---|---|---|
| `chapter.translation` | `chapter.translation` | one per file |
| `sloks[i].verse.verse_id` | `verse.verse_id` | |
| `sloks[i].verse.img_landscape` | `verse.img_landscape` | |
| `sloks[i].verse.img_square` | `verse.img_square` | |
| `sloks[i].verse.transliteration` | `verse.transliteration` | |
| `sloks[i].verse_text.speaker` | `verse_text.speaker` | `lang_code='hi'` |
| `sloks[i].verse_text.slok` | `verse_text.slok` | `lang_code='hi'` |
| `sloks[i].verse_translation.life_application` | `verse_translation.life_application` | `lang_code='en'` |

## `api/wisdom/daily.json` — wisdom screen

Script: `scripts/randomizers/wisdom_daily.py` (re-run daily by the GitHub Action). 10 randomly sampled verses, resampled every run — **not stable across days**, treat as ephemeral.

| Field (nested) | Source | Notes |
|---|---|---|
| `verse.verse_id` | `verse.verse_id` | |
| `verse.chapter_number` | `verse.chapter_number` | |
| `verse.verse_number` | `verse.verse_number` | |
| `verse.img_portrait` | `verse.img_portrait` | |
| `verse_text.slok` | `verse_text.slok` | object keyed by **every** available `lang_code` (`hi/en/be/ka`), not one language |
| `verse_translation.life_application` | `verse_translation.life_application` | `lang_code='en'` |
| `commentary.text` | `commentary.text` | default commentary (see note above), `lang_code='en'` |

## `api/home/verseofday.json` — home screen, verse of the day

Script: `scripts/randomizers/verse_of_day.py` (re-run daily by the GitHub Action). The **verse itself is a fixed constant**, `VERSE_OF_DAY_ID = "BG2.47"` — mirrors the app's own hardcoded `HomeViewModel.kt` constant, not date-derived. Only the commentator shown rotates: `epoch_day % len(commentary_rows_for_verse)`, ordered by `commentator.display_order`.

| Field (nested) | Source | Notes |
|---|---|---|
| `verse.verse_id` / `chapter_number` / `verse_number` / `transliteration` | `verse.*` | |
| `verse.img_landscape` / `img_portrait` / `img_square` | `verse.*` | |
| `verse_text.speaker` / `slok` | `verse_text.*` | `lang_code='hi'` |
| `verse_translation.life_application` | `verse_translation.life_application` | `lang_code='en'`; also the fallback for `commentary.text` if the verse has zero commentary rows |
| `commentary.text` | `commentary.text` | rotates daily by epoch day, see above; `lang_code='en'` |
| `commentator.author` | `commentator.author` | author of whichever commentary rotated in |

## `api/topics/list.json` — topics screen

Script: `api/build_topics_api.py`. One array, one object per theme (15 total). Themes carry no image of their own — each is pinned to a chapter's `img_square` via a hardcoded name→chapter map copied from the app's `HomeScreen.kt` (`topicChapterMap`), falling back to chapter 1 for any theme not in the map (currently none — all 15 are mapped).

| Field | Source | Notes |
|---|---|---|
| `name` | `theme_translation.name` | `lang_code='en'` |
| `image_square` | `chapter.img_square` | keyed by `topicChapterMap[name]`, not the theme's own row (themes have no image) |
| `verse_count` | `COUNT(*) FROM verse_theme WHERE theme_id=?` | |

## `api/meta/update.json` — per-file update epochs

Script: `scripts/build_update_meta.py`, run last in the daily workflow (after every randomizer). Not sourced from the DB — it's a filesystem scan of `api/`, `{relative_path: mtime_epoch_seconds}` for every file under `api/` except itself.
