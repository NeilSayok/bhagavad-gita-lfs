# Graph Report - .  (2026-08-03)

## Corpus Check
- 3 files · ~9,981 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 12 nodes · 14 edges · 3 communities detected
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `verse_pk()` - 4 edges
2. `verify()` - 4 edges
3. `main()` - 3 edges
4. `build()` - 2 edges
5. `dict_by_lang()` - 2 edges
6. `sh()` - 2 edges
7. `staged_files()` - 2 edges
8. `Stable INTEGER rowid: chapter * 1000 + verse. Needed as a rowid alias so the` - 1 edges
9. `Full round-trip: rebuild every source JSON from the DB and diff it.` - 1 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Communities

### Community 0 - "Community 0"
Cohesion: 0.43
Nodes (6): build(), dict_by_lang(), Full round-trip: rebuild every source JSON from the DB and diff it., Stable INTEGER rowid: chapter * 1000 + verse. Needed as a rowid alias so the, verify(), verse_pk()

### Community 1 - "Community 1"
Cohesion: 0.83
Nodes (3): main(), sh(), staged_files()

### Community 2 - "Community 2"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **2 isolated node(s):** `Stable INTEGER rowid: chapter * 1000 + verse. Needed as a rowid alias so the`, `Full round-trip: rebuild every source JSON from the DB and diff it.`
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 2`** (1 nodes): `update_bhagavadgita_chapter_18_slok_2.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What connects `Stable INTEGER rowid: chapter * 1000 + verse. Needed as a rowid alias so the`, `Full round-trip: rebuild every source JSON from the DB and diff it.` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._