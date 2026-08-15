# Graph Report - .  (2026-08-16)

## Corpus Check
- 5 files · ~12,178 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 29 nodes · 33 edges · 4 communities detected
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `verify()` - 5 edges
2. `verse_pk()` - 4 edges
3. `main()` - 4 edges
4. `main()` - 3 edges
5. `build()` - 2 edges
6. `dict_by_lang()` - 2 edges
7. `sh()` - 2 edges
8. `staged_files()` - 2 edges
9. `slugify()` - 2 edges
10. `txt()` - 2 edges

## Surprising Connections (you probably didn't know these)
- `verify()` --calls--> `dict_by_lang()`  [EXTRACTED]
  db/build_db.py → build_db.py
- `Full round-trip: rebuild every source JSON from the DB and diff it.` --rationale_for--> `verify()`  [EXTRACTED]
  build_db.py → db/build_db.py
- `verify()` --calls--> `verse_pk()`  [EXTRACTED]
  db/build_db.py → build_db.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.14
Nodes (13): ChapterEntity, ChapterTranslationEntity, CommentaryEntity, CommentatorEntity, LanguageEntity, ThemeEntity, ThemeTranslationEntity, VerseEntity (+5 more)

### Community 1 - "Community 1"
Cohesion: 0.33
Nodes (9): build(), dict_by_lang(), main(), Full round-trip: rebuild every source JSON from the DB and diff it., Stable INTEGER rowid: chapter * 1000 + verse. Needed as a rowid alias so the, slugify(), txt(), verify() (+1 more)

### Community 2 - "Community 2"
Cohesion: 0.83
Nodes (3): main(), sh(), staged_files()

### Community 3 - "Community 3"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **15 isolated node(s):** `Stable INTEGER rowid: chapter * 1000 + verse. Needed as a rowid alias so the`, `Full round-trip: rebuild every source JSON from the DB and diff it.`, `LanguageEntity`, `ChapterEntity`, `ChapterTranslationEntity` (+10 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 3`** (1 nodes): `update_bhagavadgita_chapter_18_slok_2.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What connects `Stable INTEGER rowid: chapter * 1000 + verse. Needed as a rowid alias so the`, `Full round-trip: rebuild every source JSON from the DB and diff it.`, `LanguageEntity` to the rest of the system?**
  _15 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.14 - nodes in this community are weakly interconnected._