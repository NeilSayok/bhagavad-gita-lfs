# Graph Report - .  (2026-07-03)

## Corpus Check
- 3 files · ~5,291,638 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 24 nodes · 40 edges · 4 communities detected
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
8. `output_format_with_names()` - 4 edges
9. `build_chapter_prompt()` - 4 edges
10. `build_prompt()` - 4 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `build_chapter_prompt()`  [EXTRACTED]
  TOOLS/export_excel.py → TOOLS/export_excel.py  _Bridges community 2 → community 0_

## Communities

### Community 0 - "Community 0"
Cohesion: 0.39
Nodes (8): clean(), die(), load_base_prompt(), main(), pick_english_meaning(), Parse the ```json blocks from the guidelines markdown and merge them     into a, Choose the best real English translation from {author_code: text}., write_sheet()

### Community 1 - "Community 1"
Cohesion: 0.57
Nodes (7): build_chapters(), build_sloks(), die(), gzip_file(), human(), load_json(), main()

### Community 2 - "Community 2"
Cohesion: 0.33
Nodes (6): build_chapter_prompt(), build_prompt(), output_format_with_names(), Deep-copy the shared output_format and give each image variant its own     file_, Assemble a chapter cover-image prompt JSON (as a string)., Assemble the full per-verse image-generation prompt JSON (as a string).

### Community 3 - "Community 3"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **5 isolated node(s):** `Parse the ```json blocks from the guidelines markdown and merge them     into a`, `Choose the best real English translation from {author_code: text}.`, `Deep-copy the shared output_format and give each image variant its own     file_`, `Assemble a chapter cover-image prompt JSON (as a string).`, `Assemble the full per-verse image-generation prompt JSON (as a string).`
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 3`** (1 nodes): `format_json.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main()` connect `Community 0` to `Community 2`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Why does `output_format_with_names()` connect `Community 2` to `Community 0`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Why does `build_chapter_prompt()` connect `Community 2` to `Community 0`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **What connects `Parse the ```json blocks from the guidelines markdown and merge them     into a`, `Choose the best real English translation from {author_code: text}.`, `Deep-copy the shared output_format and give each image variant its own     file_` to the rest of the system?**
  _5 weakly-connected nodes found - possible documentation gaps or missing edges._