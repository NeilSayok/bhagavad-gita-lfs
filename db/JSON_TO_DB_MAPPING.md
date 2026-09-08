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
