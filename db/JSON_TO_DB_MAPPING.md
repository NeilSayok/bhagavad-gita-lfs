# JSON → DB mapping

Source: `api/chapter/*.json` (18 files), `api/slok/*.json` (701 files), `api/slok-colophon/*.json` (18 files, excluded unless `--with-colophon`).
Built by: `db/build_db.py` → `db/schema.sql` → `db/gita.db` (schema v2, `PRAGMA user_version = 2`).

**Rule: language is a row, never a column.** Every field the source carries per-language is stored as one row per `lang_code` in a `*_translation` / `*_text` table — never as parallel `name_hi` / `name_en` columns. Adding a language = pure INSERTs, no migration. An empty/whitespace string is skipped: a missing row means "not translated yet", not NULL.

## Source is fully multilingual

All 719 slok files and all 18 chapter files carry these as `{hi, en, be, ka}` objects (verified, 100% coverage):

| File | Multilingual fields | Still single-value |
|---|---|---|
| `api/chapter/*.json` | `name`, `translation`, `transliteration`, `meaning`, `summary` | `chapter_number`, `verses_count`, `image.*` |
| `api/slok/*.json` | `speaker`, `slok`, `transliteration`, `life_application`, `word_meanings[].transliteration`, `word_meanings[].meaning`, `<commentator>.commentary` | `_id`, `chapter`, `verse`, `themes[]` (English), `word_meanings[].sanskrit`, `<commentator>.author`, `image.*` |

`<commentator>.commentary` additionally carries `sa` where a Sanskrit source text exists (9,112 rows); the other four are the translation targets.

Theme names are **English-only in the slok files** — their translations are curated separately in **`db/theme_translations.json`** (keyed by slug), which the builder joins in.

## language

Not derived from JSON — hardcoded in `build_db.py`: `sa, hi, en, be, ka` (`is_script_only=1` for `sa` only).

## `api/chapter/*.json` → `chapter` + `chapter_translation`

`chapter` holds only what is genuinely language-independent; every text field moved to `chapter_translation` in v2.

| JSON field | Column | Table |
|---|---|---|
| `chapter_number` | `chapter_number` (PK) | `chapter` |
| `verses_count` | `verses_count` | `chapter` |
| — (generated) | `img_landscape/portrait/square` = `chapters/{size}/chapter_<n>/<variant>/img.png` | `chapter` |
| `name.<lang>` | `name` | `chapter_translation` |
| `translation.<lang>` | `translation` | `chapter_translation` |
| `transliteration.<lang>` | `transliteration` | `chapter_translation` |
| `meaning.<lang>` | `meaning` | `chapter_translation` |
| `summary.<lang>` | `summary` | `chapter_translation` |

`chapter_translation` PK is `(chapter_number, lang_code)` — one row per language present in *any* of the five fields. Current: 18 rows × 4 languages.

## `api/slok/*.json` → `verse` + related tables

| JSON field | Column | Table |
|---|---|---|
| `_id` | `verse_id` (PK, e.g. `BG1.1`) | `verse` |
| `chapter` | `chapter_number` (FK → `chapter`) | `verse` |
| `verse` | `verse_number` | `verse` |
| — (generated) | `img_landscape/portrait/square` = `sloks/{size}/chapter_<c>/slok_<v>/<variant>/img.png` | `verse` |

### `speaker` + `slok` + `transliteration` → `verse_text` (PK `verse_id, lang_code`)

The same Sanskrit verse rendered per script — **not** a meaning translation. One row per language present in any of the three fields. Current: 701 × 4.

| JSON field | Column |
|---|---|
| `speaker.<lang>` | `speaker` |
| `slok.<lang>` | `slok` |
| `transliteration.<lang>` | `transliteration` (v2: moved off `verse`) |

### `life_application` → `verse_translation` (PK `verse_id, lang_code`)

Meaning-level prose, one row per language. Current: 701 × 4 (was English-only before the source was translated).

| JSON field | Column |
|---|---|
| `life_application.<lang>` | `life_application` |

### `themes[]` → `theme` / `theme_translation` / `verse_theme`

- `theme` is built once globally: first occurrence across all slok files wins the `theme_id`; `slug` = slugified English name.
- `theme_translation` gets one row per language from **`db/theme_translations.json`** (`{slug: {hi, en, be, ka}}`), falling back to the raw English name if a slug is absent. Current: 15 × 4.
- `verse_theme` gets one row per array element, `position` = array index (preserves JSON order).

| JSON field | Column | Table |
|---|---|---|
| `themes[i]` (name, dedup'd) | `theme_id` (assigned), `slug` | `theme` |
| `db/theme_translations.json[slug].<lang>` | `name` | `theme_translation` |
| index `i` | `position`; `theme_id` | `verse_theme` |

### `word_meanings[]` → `word_meaning` / `word_meaning_translation`

One `word_meaning` row per array element, `position` = array index. `sanskrit` is the only field that isn't translated, so it's the only one left on the parent row in v2.

| JSON field | Column | Table |
|---|---|---|
| `word_meanings[i].sanskrit` | `sanskrit` | `word_meaning` (PK `verse_id, position`) |
| `word_meanings[i].transliteration.<lang>` | `transliteration` (v2: moved off `word_meaning`) | `word_meaning_translation` (PK `verse_id, position, lang_code`) |
| `word_meanings[i].meaning.<lang>` | `meaning` | `word_meaning_translation` |

Current: 7,964 `word_meaning` rows, 7,964 × 4 translations.

### `<commentator_key>.author` → `commentator` (global, not per-verse)

For each of the 22 commentator keys (`tej, siva, purohit, chinmay, san, adi, gambir, madhav, anand, rams, raman, abhinav, sankar, jaya, vallabh, ms, srid, dhan, venkat, puru, neel, prabhu`), the **most frequent** non-blank `author` value across all slok files is the canonical `author` (fixes blocks with a missing/inconsistent author field). `display_order` = index in the fixed key list above.

### `<commentator_key>.commentary.<lang>` → `commentary` (PK `verse_id, commentator_key, lang_code`)

One row per (commentator × language) pair present, skipped if blank. Current: 15,422 × 4 + 9,112 `sa`.

| JSON field | Column |
|---|---|
| `<key>.commentary.<lang>` | `text` |

## Integrity checks run by `build_db.py`'s `verify()`

- exactly 18 `chapter` rows, `n_sloks` `verse` rows, 22 `commentator` rows
- verse numbers contiguous `1..count` within every chapter (colophons excluded by default)
- zero foreign-key violations (`PRAGMA foreign_key_check`)
- `commentary` spans all 5 `lang_code` values
- **every translated table carries all of `hi/en/be/ka`** — `chapter_translation`, `verse_text`, `verse_translation`, `theme_translation`, `word_meaning_translation`. This is what catches a regression back to English-only.

`verify()` also prints a per-table `lang_code` row-count breakdown on every build.

---

# DB → static API JSON mapping

Every screen reads a **precomputed static JSON file** under `api/`, generated from `db/gita.db`. Nothing is computed on-device. `api/meta/update.json` records a last-modified epoch per file under `api/`, so a client can cheaply detect which changed.

**Every text field below is a `{hi, en, be, ka}` object**, ordered `hi, en, be, ka`, sourced from the per-language rows above. The three `build_*_api.py` scripts reproduce the committed output byte-identically, so regenerating is non-destructive.

Default commentary note: where a single commentary is needed (home/wisdom), the pick is constrained to commentators whose block has **all four languages present**, in `commentator.display_order`.

## `api/reading/all.json` — reading screen

Script: `scripts/build_reading_api.py`. One array: 701 verse objects, plus a colophon block after each chapter's last verse (18 total, read straight from `api/slok-colophon/*.json` since colophons are excluded from the DB) = 719 entries.

| Field (nested) | Source |
|---|---|
| `chapter.translation` | `chapter_translation.translation` |
| `verse.verse_id` / `chapter_number` / `verse_number` | `verse.*` |
| `verse.transliteration` | `verse_text.transliteration` |
| `verse.img_landscape` / `img_square` | `verse.*` |
| `verse_text.speaker` / `slok` | `verse_text.*` |
| `verse_translation.life_application` | `verse_translation.life_application` |

Colophon entries carry `chapter.translation` plus `colophon.{verse_id, transliteration, speaker, slok}`.

## `api/chapter-slok/<chapter_number>/list.json` — chapter screen

Script: `scripts/build_chapter_api.py`. One file per chapter (18), each `{ chapter: {translation}, sloks: [...] }`. Same field sources as reading, minus `chapter_number`/`verse_number`.

## `api/wisdom/daily.json` — wisdom screen

Script: `scripts/randomizers/wisdom_daily.py` (re-run daily). 10 randomly sampled verses, resampled every run — **not stable across days**.

Selection rules: the commentary must be **90–200 characters in every one of the four languages** (~3–4 lines on a card — checking only English lets a much longer hi/be/ka rendering through); it must not be a **stub** (cross-reference or "did not comment on this sloka" placeholder — 861 such blocks exist in the corpus and are real source text, just not renderable); the verse must **never** be the one in `api/home/verseofday.json`, which is read at runtime; `slok`, `life_application` and `commentary` must all have all four languages, else the verse is skipped.

| Field (nested) | Source |
|---|---|
| `verse.verse_id` / `chapter_number` / `verse_number` / `img_portrait` | `verse.*` |
| `verse_text.slok` | `verse_text.slok` |
| `verse_translation.life_application` | `verse_translation.life_application` |
| `commentary.text` | `commentary.text` (first fully-translated commentator in `display_order` meeting the length window) |
| `commentator.author` | `commentator.author` |

## `api/home/verseofday.json` — home screen, verse of the day

Script: `scripts/randomizers/verse_of_day.py` (re-run daily). **Both the verse and the commentator rotate by epoch day.** The verse is drawn from a pool of **683** verses — those with all four languages on `speaker`/`slok`/`transliteration`/`life_application` **and** at least one card-ready commentary — shuffled once with a fixed seed (`SHUFFLE_SEED`) then indexed `epoch_day % 683`. Deterministic, so re-running the pipeline twice in a day yields an identical file, and the cycle runs 683 days before repeating. The commentator rotates separately over that verse's card-ready blocks: `epoch_day % len(candidates)`, ordered by `commentator.display_order`.

"Card-ready" is the same bar wisdom uses: all four languages present, **each** language 90–200 characters, and not a stub.

Ordering note: `wisdom_daily.py` reads this file to avoid reusing today's verse, so `verse_of_day.py` must run first. The workflow's `for f in scripts/randomizers/*.py` loop is alphabetical, which already puts it ahead.

| Field (nested) | Source |
|---|---|
| `verse.verse_id` / `chapter_number` / `verse_number` / `img_*` | `verse.*` |
| `verse.transliteration` | `verse_text.transliteration` |
| `verse_text.speaker` / `slok` | `verse_text.*` |
| `verse_translation.life_application` | `verse_translation.life_application` |
| `commentary.text` | `commentary.text`, rotated daily |
| `commentator.author` | `commentator.author` |

## `api/topics/list.json` — topics screen

Script: `scripts/build_topics_api.py`. One array, one object per theme (15). Themes have no image of their own — each is pinned to a chapter's `img_square` via a hardcoded English-name→chapter map copied from the app's `HomeScreen.kt` (`topicChapterMap`), fallback chapter 1.

| Field | Source |
|---|---|
| `name` | `theme_translation.name` (all 4 languages) |
| `image_square` | `chapter.img_square`, keyed by `topicChapterMap[name.en]` |
| `verse_count` | `COUNT(*) FROM verse_theme WHERE theme_id=?` |
| `sloks` | `verse_theme.verse_id`, `WHERE theme_id=? ORDER BY position` |

## `api/meta/update.json` — per-file update epochs

Script: `scripts/build_update_meta.py`, run last in both workflows. Not sourced from the DB — a filesystem scan of `api/`: `{relative_path: mtime_epoch_seconds}` for every file under `api/` except itself.

## `api/chapter/*.json`, `api/slok/*.json`, `api/slok-colophon/*.json` — source, not generated

Not built by any script. These **are** the source of truth the DB is built from (see the first half of this document), committed under `api/` so clients can fetch raw per-verse data directly. `api/meta/update.json` tracks their mtimes like every other file under `api/`.
