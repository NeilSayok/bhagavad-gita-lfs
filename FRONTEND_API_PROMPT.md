# Migrating BhagavadGita (V2 KMP app) to the static JSON API

Paste this to the frontend session.

---

The data layer has moved. The app must stop deriving content locally and instead
read precomputed static JSON. Read this fully before changing code.

## What changed

Content is now generated server-side and committed as static JSON under `api/`
in the dataset repo (NeilSayok/bhagavad-gita-lfs). A GitHub Action regenerates
it daily. The app fetches these files over HTTPS and renders them as-is.

Base URL: `https://neilsayok.github.io/bhagavad-gita-lfs`

## Endpoints

| Path | Shape |
|---|---|
| `api/reading/all.json` | array, 719 entries |
| `api/chapter-slok/<1-18>/list.json` | `{chapter, sloks[]}` |
| `api/home/verseofday.json` | single object |
| `api/wisdom/daily.json` | array of 10 |
| `api/topics/list.json` | array of 15 |
| `api/meta/update.json` | `{ "<path relative to api/>": <mtime epoch seconds> }` |

## Every text field is localized

`LocalizedText` = `{"hi": str, "en": str, "be": str, "ka": str}` — always all four
keys, in that order. There is no flat-string variant anywhere. Model it as one type:

```kotlin
@Serializable
data class LocalizedText(val hi: String, val en: String, val be: String, val ka: String) {
    operator fun get(lang: String): String = when (lang) {
        "hi" -> hi; "be" -> be; "ka" -> ka; else -> en
    }
}
```

Shapes (`L` = LocalizedText):

```
reading/all.json          [ verse-entry | colophon-entry, ... ]
  verse-entry    { chapter:{translation:L},
                   verse:{verse_id, chapter_number, verse_number, transliteration:L,
                          img_landscape, img_square},
                   verse_text:{speaker:L, slok:L},
                   verse_translation:{life_application:L} }
  colophon-entry { chapter:{translation:L},
                   colophon:{verse_id, transliteration:L, speaker:L, slok:L} }

chapter-slok/<n>/list.json { chapter:{translation:L},
                             sloks:[ {verse:{verse_id, img_landscape, img_square,
                                             transliteration:L},
                                      verse_text:{speaker:L, slok:L},
                                      verse_translation:{life_application:L}} ] }

home/verseofday.json      { verse:{verse_id, chapter_number, verse_number,
                                   transliteration:L, img_landscape, img_portrait,
                                   img_square},
                            verse_text:{speaker:L, slok:L},
                            verse_translation:{life_application:L},
                            commentary:{text:L}, commentator:{author: String} }

wisdom/daily.json         [ {verse:{verse_id, chapter_number, verse_number, img_portrait},
                             verse_text:{slok:L},
                             verse_translation:{life_application:L},
                             commentary:{text:L}, commentator:{author: String}} x10 ]

topics/list.json          [ {name:L, image_square, verse_count:Int, sloks:[verse_id]} x15 ]
```

## Rule 1 — do NOT compute the daily rotation

`home/verseofday.json` already contains the resolved verse *and* commentary for today —
both rotate server-side, keyed on epoch day. Render what the file gives you directly.

**Delete** `HomeViewModel.kt`'s hardcoded `VERSE_OF_DAY_ID` and its
`currentEpochDay() % commentary.size` logic. If the app recomputes any of this it will
be wrong several ways: it rolls over at 00:00 UTC while the file is regenerated at
00:00 IST (5h30m disagreement); it would index into the app's own lists whereas the
published indices were computed over only the verses/commentators having all four
languages; and the verse is no longer a constant, so a pinned id would be stale.

No timezone handling is needed anywhere for content selection. Do not add an IST check.

## Rule 2 — cache invalidation uses `meta/update.json`, not the clock

Fetch `api/meta/update.json`, compare each path's epoch against the epoch you stored
when you last downloaded that file. Larger = refetch. This is immune to device
timezone and clock skew, which a "is it past midnight?" check is not.

`reading/all.json` is large — cache it (see the Room section below) and only refetch when
its epoch changes. `home/verseofday.json` and `wisdom/daily.json` change daily; everything
else changes rarely.

## Rule 3 — image paths contain a `{size}` placeholder

`img_*` / `image_square` values look like:

```
sloks/{size}/chapter_1/slok_1/landscape/img.png
chapters/{size}/chapter_7/square/img.png
```

Substitute `{size}` with the desired variant before prefixing the image base URL.
These are relative paths, never full URLs.

## Rule 4 — colophon entries in reading/all.json

`reading/all.json` has 719 entries: **701 verses + 18 colophons**. A colophon is the
closing "OM tatsat…" line of a chapter — it appears immediately after that chapter's
last verse and has a `colophon` key instead of `verse`/`verse_text`/`verse_translation`.

Discriminate on key presence (`"verse" in entry` vs `"colophon" in entry`) and render
colophons as a chapter-end marker, not as a numbered verse. They have no
`life_application`, no `verse_number`, and no images.

Note 701, not 719, is the real verse count — colophons are excluded from verse
numbering, so chapter 1 has verses 1..47 plus one colophon.

## Rule 5 — topics reference verses by id

`topics/list.json`'s `sloks` is an array of `verse_id` strings (`"BG9.34"`), not
embedded verse objects. Resolve them against data you already hold from
`reading/all.json` or `chapter-slok/`. `verse_count == sloks.size`.

## Room is now the JSON cache, not the content store

Keep Room, but repurpose it. It no longer models Gita content — it caches the fetched
JSON payloads and the epoch each was fetched at. One table is enough:

```kotlin
@Entity(tableName = "api_cache")
data class ApiCacheEntity(
    @PrimaryKey val path: String,   // "home/verseofday.json", relative to api/
    val epoch: Long,                // value from meta/update.json when this was stored
    val json: String,               // raw response body
)
```

Read path: look up `path` → if absent, fetch; if present, deserialize `json` and render
immediately, then compare `epoch` against the current `meta/update.json` and refetch in
the background only when it is larger. That gives offline-first rendering for free.

Consequently, **delete**: the bundled `gita.db` asset from `androidApp/src/main/assets/`
and `iosApp/iosApp/Resources/`, all the old content entities (`ChapterEntity`,
`VerseEntity`, `VerseTextEntity`, `VerseTranslationEntity`, commentary/theme entities),
their DAOs, and the prepopulated-database copy logic in `DatabaseBuilderFactory`
(both `.android.kt` and `.ios.kt`) — Room now creates an empty DB normally. Keep the
`read_verse` / `bookmark` tables; those are user state, unrelated to this migration.

Ignore `db/room/GitaEntities.kt` in the dataset repo. It mirrors the old pre-v2 content
schema and is obsolete for this app.

## Task

1. Add serialization models for the above (one `LocalizedText`, reused everywhere).
2. Add a repository that fetches these files and caches them in Room (`api_cache`),
   keyed on `meta/update.json` epochs — serve cache first, refetch only on a newer epoch.
3. Wire the existing screens (home, reading, chapters, wisdom, topics) to it.
4. Remove the local daily-rotation logic and any per-language branching that assumed
   single-language strings.
5. Resolve the display language from the user's app-language setting by indexing
   `LocalizedText`, defaulting to `en`.

Do not add timezone logic. Do not recompute which commentary or which verse to show.
