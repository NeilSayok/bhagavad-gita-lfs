# Graph Report - .  (2026-09-09)

## Corpus Check
- 17 files · ~35,211 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 78 nodes · 89 edges · 15 communities detected
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 10 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `verify()` - 5 edges
2. `Build a verse-centric ObjectBox store from slok/*.json.  Writes one Slok record` - 5 edges
3. `Split text into pieces that fit the embedding model's context window.` - 5 edges
4. `verse_pk()` - 4 edges
5. `Slok` - 4 edges
6. `Embedding` - 4 edges
7. `main()` - 4 edges
8. `main()` - 3 edges
9. `main()` - 3 edges
10. `Semantic search test against the ObjectBox store built by build_objectbox.py.  U` - 3 edges

## Surprising Connections (you probably didn't know these)
- `verify()` --calls--> `dict_by_lang()`  [EXTRACTED]
  db/build_db.py → build_db.py
- `Full round-trip: rebuild every source JSON from the DB and diff it.` --rationale_for--> `verify()`  [EXTRACTED]
  build_db.py → db/build_db.py
- `verify()` --calls--> `verse_pk()`  [EXTRACTED]
  db/build_db.py → build_db.py
- `Semantic search test against the ObjectBox store built by build_objectbox.py.  U` --uses--> `Slok`  [INFERRED]
  embedding-pipeline/objectbox/test_search.py → embedding-pipeline/objectbox/model.py
- `Semantic search test against the ObjectBox store built by build_objectbox.py.  U` --uses--> `Embedding`  [INFERRED]
  embedding-pipeline/objectbox/test_search.py → embedding-pipeline/objectbox/model.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.14
Nodes (13): ChapterEntity, ChapterTranslationEntity, CommentaryEntity, CommentatorEntity, LanguageEntity, ThemeEntity, ThemeTranslationEntity, VerseEntity (+5 more)

### Community 1 - "Community 1"
Cohesion: 0.29
Nodes (11): chunk_text(), main(), Build a verse-centric ObjectBox store from slok/*.json.  Writes one Slok record, Split text into pieces that fit the embedding model's context window., verify(), Commentary, Embedding, Verse-centric ObjectBox entities for the Bhagavad Gita corpus.  No Chapter or Th (+3 more)

### Community 2 - "Community 2"
Cohesion: 0.33
Nodes (9): build(), dict_by_lang(), main(), Full round-trip: rebuild every source JSON from the DB and diff it., Stable INTEGER rowid: chapter * 1000 + verse. Needed as a rowid alias so the, slugify(), txt(), verify() (+1 more)

### Community 3 - "Community 3"
Cohesion: 0.4
Nodes (3): add_images(), main(), Add an "image" block to every chapter/*.json and slok/*.json file.  Paths only (

### Community 4 - "Community 4"
Cohesion: 0.6
Nodes (4): load_rows(), main(), Embed verse + commentary text from the slok/*.json corpus with embeddinggemma-30, verify()

### Community 5 - "Community 5"
Cohesion: 0.83
Nodes (3): main(), sh(), staged_files()

### Community 6 - "Community 6"
Cohesion: 0.67
Nodes (3): epoch_day(), main(), Randomizer: verse-of-the-day -> api/home/verseofday.json.  Verse itself is a fix

### Community 7 - "Community 7"
Cohesion: 0.67
Nodes (1): Convert embeddings.parquet into embeddings.jsonl (one row per line) for the Kotl

### Community 8 - "Community 8"
Cohesion: 1.0
Nodes (2): main(), search()

### Community 9 - "Community 9"
Cohesion: 0.67
Nodes (1): Build api/meta/update.json: last-modified epoch (seconds) for every file under a

### Community 10 - "Community 10"
Cohesion: 0.67
Nodes (1): Randomizer: pick 10 random verses for the wisdom screen -> api/wisdom/daily.json

### Community 11 - "Community 11"
Cohesion: 0.67
Nodes (1): Build api/reading/all.json (static, precomputed) from db/gita.db.

### Community 12 - "Community 12"
Cohesion: 0.67
Nodes (1): Build api/chapter/<number>/list.json (static, precomputed) from db/gita.db. One

### Community 13 - "Community 13"
Cohesion: 0.67
Nodes (1): Build api/topics/list.json (static, precomputed) from db/gita.db.  Themes carry

### Community 14 - "Community 14"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
- **25 isolated node(s):** `Add an "image" block to every chapter/*.json and slok/*.json file.  Paths only (`, `Stable INTEGER rowid: chapter * 1000 + verse. Needed as a rowid alias so the`, `Full round-trip: rebuild every source JSON from the DB and diff it.`, `Embed verse + commentary text from the slok/*.json corpus with embeddinggemma-30`, `Convert embeddings.parquet into embeddings.jsonl (one row per line) for the Kotl` (+20 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 14`** (1 nodes): `update_bhagavadgita_chapter_18_slok_2.py`
=======
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
- **Thin community `Community 0`** (2 nodes): `validate_slok.py`, `validate()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 1`** (2 nodes): `run_scripts.py`, `run_subagent_scripts()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 2`** (2 nodes): `scratchpad_fill.py`, `fill()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 3`** (1 nodes): `update_bhagavadgita_chapter_18_slok_2.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 4`** (1 nodes): `fill_ch4_v6_to_v10.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 5`** (1 nodes): `fill_ch9_v11_to_v15.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 6`** (1 nodes): `fill_ch3_v32_to_v36.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 7`** (1 nodes): `fill_ch8_v25_to_v28.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 8`** (1 nodes): `fill_ch5_v30.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 9`** (1 nodes): `fill_ch3_v37_to_v40.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 10`** (1 nodes): `fill_ch5_v1_to_v5.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 11`** (1 nodes): `fill_ch8_v4_v5.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 12`** (1 nodes): `fill_ch4_v31_to_v35.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 13`** (1 nodes): `fill_ch5_v6_to_v11.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 14`** (1 nodes): `fill_ch4_v16_to_v20.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 15`** (1 nodes): `fill_ch8_v21_to_v24.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 16`** (1 nodes): `fill_ch8_v12_to_v15.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 17`** (1 nodes): `fill_ch6_v26_to_v30.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 18`** (1 nodes): `fill_ch7_v16_to_v20.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (1 nodes): `fill_ch7_colophon.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (1 nodes): `fill_ch4_v11_to_v15.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (1 nodes): `fill_ch7_v22_to_v25.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (1 nodes): `fill_ch6_v41_to_v47.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (1 nodes): `fix_ch9_v31_to_v34.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 24`** (1 nodes): `fill_ch7_v1_v2.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (1 nodes): `fill_ch3_v41_to_v44.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (1 nodes): `fill_ch3_v17_to_v21.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (1 nodes): `fill_ch8_v6_to_v10.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 28`** (1 nodes): `fill_ch3_v12_to_v16.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (1 nodes): `fill_ch9_v16_to_v20.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (1 nodes): `fill_ch6_v21_to_v25.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (1 nodes): `fill_ch7_v3_to_v5.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (1 nodes): `fill_ch9_v31_to_v34.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (1 nodes): `fill_ch7_v17_to_v20.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (1 nodes): `fill_ch6_v1_to_v5.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (1 nodes): `fill_ch7_v11_to_v15.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (1 nodes): `fill_ch4_v36_to_v40.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (1 nodes): `fill_ch8_v9_v10.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (1 nodes): `fill_ch3_v7_to_v11.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (1 nodes): `fill_ch5_v22_to_v26.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (1 nodes): `fill_ch5_v12_to_v16.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 41`** (1 nodes): `fill_ch5_v17_to_v21.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 42`** (1 nodes): `fill_ch4_v41_to_v43.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 43`** (1 nodes): `fill_ch7_v7_to_v10.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (1 nodes): `fill_ch7_v27_to_v30.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (1 nodes): `fix_ch8_gaps.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (1 nodes): `fill_ch8_v1_to_v5.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (1 nodes): `fill_ch7_v21_to_v25.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (1 nodes): `fill_ch18_v6.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (1 nodes): `fix_ch9_all_remaining.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 50`** (1 nodes): `fill_ch6_v11_to_v15.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (1 nodes): `fill_ch9_v5_v9_v10.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 52`** (1 nodes): `fill_ch6_v36_to_v40.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 53`** (1 nodes): `fill_ch4_v1_to_v5.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 54`** (1 nodes): `fill_ch3_v22_to_v26.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 55`** (1 nodes): `fill_ch8_v16_to_v20.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 56`** (1 nodes): `fill_ch3_v27_to_v31.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 57`** (1 nodes): `fill_ch4_v21_to_v25.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 58`** (1 nodes): `fill_ch9_v26_to_v30.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 59`** (1 nodes): `fill_ch7_v12_to_v15.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 60`** (1 nodes): `fill_ch6_v16_to_v20.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 61`** (1 nodes): `fill_ch9_v3_v4_v5_v9_v10.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 62`** (1 nodes): `fill_ch8_v26_to_v28.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 63`** (1 nodes): `fill_ch6_v31_to_v35.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 64`** (1 nodes): `fill_ch7_v6_to_v10.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 65`** (1 nodes): `fill_ch7_v26_to_v30.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 66`** (1 nodes): `fill_ch8_v29_colophon.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 67`** (1 nodes): `fill_ch6_v2_to_v5.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 68`** (1 nodes): `fill_missing_prabhu_colophons.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 69`** (1 nodes): `fill_ch6_v6_to_v10.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 70`** (1 nodes): `fill_ch9_v4_v5_v9_v10.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 71`** (1 nodes): `fill_ch8_v7_v8.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 72`** (1 nodes): `fill_ch8_v11_to_v15.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 73`** (1 nodes): `fill_ch8_v2_v3.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 74`** (1 nodes): `fill_ch8_v17_to_v20.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 75`** (1 nodes): `fill_ch6_colophon.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 76`** (1 nodes): `fill_ch4_v26_to_v30.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 77`** (1 nodes): `fill_ch9_v21_to_v25.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 78`** (1 nodes): `fill_ch5_v27_to_v29.py`
>>>>>>> Stashed changes
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Are the 4 inferred relationships involving `Build a verse-centric ObjectBox store from slok/*.json.  Writes one Slok record` (e.g. with `Slok` and `WordMeaning`) actually correct?**
  _`Build a verse-centric ObjectBox store from slok/*.json.  Writes one Slok record` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `Split text into pieces that fit the embedding model's context window.` (e.g. with `Slok` and `WordMeaning`) actually correct?**
  _`Split text into pieces that fit the embedding model's context window.` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `Slok` (e.g. with `Semantic search test against the ObjectBox store built by build_objectbox.py.  U` and `Build a verse-centric ObjectBox store from slok/*.json.  Writes one Slok record`) actually correct?**
  _`Slok` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Add an "image" block to every chapter/*.json and slok/*.json file.  Paths only (`, `Stable INTEGER rowid: chapter * 1000 + verse. Needed as a rowid alias so the`, `Full round-trip: rebuild every source JSON from the DB and diff it.` to the rest of the system?**
  _25 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.14 - nodes in this community are weakly interconnected._