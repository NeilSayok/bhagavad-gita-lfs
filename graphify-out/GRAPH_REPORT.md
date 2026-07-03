# Graph Report - .  (2026-06-28)

## Corpus Check
- 3 files · ~3,074,857 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 22 nodes · 36 edges · 7 communities detected
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `main()` - 7 edges
2. `main()` - 5 edges
3. `die()` - 4 edges
4. `load_json()` - 4 edges
5. `build_chapters()` - 4 edges
6. `build_sloks()` - 4 edges
7. `load_base_prompt()` - 4 edges
8. `die()` - 3 edges
9. `pick_english_meaning()` - 3 edges
10. `build_chapter_prompt()` - 3 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `pick_english_meaning()`  [EXTRACTED]
  TOOLS/export_excel.py → TOOLS/export_excel.py  _Bridges community 4 → community 1_
- `main()` --calls--> `build_chapter_prompt()`  [EXTRACTED]
  TOOLS/export_excel.py → TOOLS/export_excel.py  _Bridges community 3 → community 1_
- `main()` --calls--> `build_prompt()`  [EXTRACTED]
  TOOLS/export_excel.py → TOOLS/export_excel.py  _Bridges community 5 → community 1_
- `main()` --calls--> `write_sheet()`  [EXTRACTED]
  TOOLS/export_excel.py → TOOLS/export_excel.py  _Bridges community 2 → community 1_

## Communities

### Community 0 - "Community 0"
Cohesion: 0.57
Nodes (7): build_chapters(), build_sloks(), die(), gzip_file(), human(), load_json(), main()

### Community 1 - "Community 1"
Cohesion: 0.67
Nodes (4): die(), load_base_prompt(), main(), Parse the ```json blocks from the guidelines markdown and merge them     into a

### Community 2 - "Community 2"
Cohesion: 1.0
Nodes (2): clean(), write_sheet()

### Community 3 - "Community 3"
Cohesion: 1.0
Nodes (2): build_chapter_prompt(), Assemble a chapter cover-image prompt JSON (as a string).

### Community 4 - "Community 4"
Cohesion: 1.0
Nodes (2): pick_english_meaning(), Choose the best real English translation from {author_code: text}.

### Community 5 - "Community 5"
Cohesion: 1.0
Nodes (2): build_prompt(), Assemble the full per-verse image-generation prompt JSON (as a string).

### Community 6 - "Community 6"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **4 isolated node(s):** `Parse the ```json blocks from the guidelines markdown and merge them     into a`, `Choose the best real English translation from {author_code: text}.`, `Assemble a chapter cover-image prompt JSON (as a string).`, `Assemble the full per-verse image-generation prompt JSON (as a string).`
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 3`** (2 nodes): `build_chapter_prompt()`, `Assemble a chapter cover-image prompt JSON (as a string).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 4`** (2 nodes): `pick_english_meaning()`, `Choose the best real English translation from {author_code: text}.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 5`** (2 nodes): `build_prompt()`, `Assemble the full per-verse image-generation prompt JSON (as a string).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 6`** (1 nodes): `format_json.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main()` connect `Community 1` to `Community 2`, `Community 3`, `Community 4`, `Community 5`?**
  _High betweenness centrality (0.093) - this node is a cross-community bridge._
- **Why does `load_base_prompt()` connect `Community 1` to `Community 2`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Why does `pick_english_meaning()` connect `Community 4` to `Community 1`, `Community 2`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **What connects `Parse the ```json blocks from the guidelines markdown and merge them     into a`, `Choose the best real English translation from {author_code: text}.`, `Assemble a chapter cover-image prompt JSON (as a string).` to the rest of the system?**
  _4 weakly-connected nodes found - possible documentation gaps or missing edges._