# Graph Report - .  (2026-06-22)

## Corpus Check
- Corpus is ~1,408 words - fits in a single context window. You may not need a graph.

## Summary
- 16 nodes · 11 edges · 5 communities detected
- Extraction: 73% EXTRACTED · 27% INFERRED · 0% AMBIGUOUS · INFERRED: 3 edges (avg confidence: 0.77)
- Token cost: 0 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `Bhagavad Gita Translations and Commentary Dataset` - 4 edges
2. `Contributing Guidelines` - 4 edges
3. `Code of Conduct` - 2 edges
4. `Bhagavad Gita API` - 2 edges
5. `format_json.py JSON Formatter` - 1 edges
6. `GitHub API Source Code Repository` - 1 edges
7. `Featured Translation and Commentary Authors` - 1 edges
8. `GitHub Flow Workflow` - 1 edges
9. `MIT Software License` - 1 edges
10. `Graphify Knowledge Graph Integration` - 1 edges

## Surprising Connections (you probably didn't know these)
- `format_json.py JSON Formatter` --semantically_similar_to--> `Bhagavad Gita Translations and Commentary Dataset`  [INFERRED] [semantically similar]
  TOOLS/format_json.py → README.md
- `Graphify Knowledge Graph Integration` --references--> `Bhagavad Gita Translations and Commentary Dataset`  [INFERRED]
  CLAUDE.md → README.md

## Hyperedges (group relationships)
- **Contribution and Community Governance Framework** — code_of_conduct, contributing_guidelines, pull_request_workflow, community_standards [EXTRACTED 0.95]
- **Bhagavad Gita Dataset and API Ecosystem** — bhagavad_gita_dataset, bhagavad_gita_api, github_api_source, featured_authors [EXTRACTED 1.00]

## Communities

### Community 0 - "Dataset & API Ecosystem"
Cohesion: 0.33
Nodes (6): Bhagavad Gita API, Bhagavad Gita Translations and Commentary Dataset, Featured Translation and Commentary Authors, format_json.py JSON Formatter, GitHub API Source Code Repository, Graphify Knowledge Graph Integration

### Community 1 - "Contribution Process"
Cohesion: 0.4
Nodes (5): Contributing Guidelines, Facebook Draft Contributing Guidelines Reference, GitHub Flow Workflow, MIT Software License, Pull Request Contribution Workflow

### Community 2 - "Community Governance"
Cohesion: 0.67
Nodes (3): Code of Conduct, Community Standards and Conduct, Dev.to Code of Conduct Source

### Community 3 - "Data Formatting Tool"
Cohesion: 1.0
Nodes (0): 

### Community 4 - "Security"
Cohesion: 1.0
Nodes (1): Security Policy and Vulnerability Reporting

## Knowledge Gaps
- **11 isolated node(s):** `format_json.py JSON Formatter`, `GitHub API Source Code Repository`, `Featured Translation and Commentary Authors`, `GitHub Flow Workflow`, `MIT Software License` (+6 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Data Formatting Tool`** (1 nodes): `format_json.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Security`** (1 nodes): `Security Policy and Vulnerability Reporting`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Are the 2 inferred relationships involving `Bhagavad Gita Translations and Commentary Dataset` (e.g. with `format_json.py JSON Formatter` and `Graphify Knowledge Graph Integration`) actually correct?**
  _`Bhagavad Gita Translations and Commentary Dataset` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `format_json.py JSON Formatter`, `GitHub API Source Code Repository`, `Featured Translation and Commentary Authors` to the rest of the system?**
  _11 weakly-connected nodes found - possible documentation gaps or missing edges._