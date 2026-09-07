# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A pure JSON dataset of the Bhagavad Gita — no build, no app code, no package manager. Two directories:

- `chapter/bhagavadgita_chapter_<C>.json` (18 files) — per-chapter metadata: `chapter_number`, `verses_count`, `name` (Sanskrit), `translation`, `transliteration`, `meaning{en,hi}`, `summary{en,hi}`.
- `slok/bhagavadgita_chapter_<C>_slok_<N>.json` (719 files) — one file per verse, the actual unit of work. Each file is independent; no cross-file references except shared terminology.

There is no test suite, linter, or build command — validation means "does it parse as valid JSON and are the fields correctly populated," done with small ad-hoc Python scripts (`json.load`/`json.dump`), not a project-wide test runner.

## Slok file schema

```
_id, chapter, verse          — internal, never modify
speaker { hi, en, be, ka }   — transliteration only, NOT meaning translation (en = readable name, not IAST)
slok    { hi, en, be, ka }   — same Sanskrit verse transliterated per script (en = IAST romanization)
transliteration               — legacy top-level field, kept as-is, redundant with slok.en
<commentator key>: {
  "author": "...",
  "commentary": { "hi": "...", "en": "...", "be": "...", "ka": "...", "sa": "..." }  // sa last, only if block originally had Sanskrit source
}
```

Up to 23 commentator keys per file: `tej, siva, purohit, chinmay, san, adi, gambir, madhav, anand, rams, raman, abhinav, sankar, jaya, vallabh, ms, srid, dhan, venkat, puru, neel, prabhu` (prabhu present in 700/719 files).

Original source-field mapping (pre-restructure, historical): `ht`/`hc` → `hi`, `et`/`ec` → `en`, `sc` → `sa`.

## Translation workflow

Full plan, glossary, and per-verse progress log: `.claude/TRANSLATION-PLAN.md`. Read it before doing any translation work — it has the current chapter/verse position and hard-won lessons from past runs.

Per-language sub-agents live in `.claude/agents/{EN,HI,BE,KA,SA}-TRANSLATION-SUBAGENT.md`. Architecture: one orchestrator session dispatches one whole slok file at a time to exactly one language agent; that agent fills only its language's empty slots by meaning (never word-for-word), never touches other languages or the internal/`speaker`/`slok` fields, and never spawns further sub-agents. `sa` is preserved only — never generated (Sanskrit is the source of truth, not a translation target).

Hard rules learned from past mistakes (all detailed in the plan doc's Issues/Lessons sections):

- **Never trust an agent's "completed" report.** Always reopen the file after and verify: valid JSON, zero empty target-language slots, and every value is `str` (a stray trailing comma after a dict value silently turns it into a 1-element list, which `json.dump` serializes as a JSON array — this has happened repeatedly).
- Write JSON via Python (`json.load` → mutate → `json.dump(ensure_ascii=False, indent=4)` + trailing newline), never hand-edit strings — avoids Unicode/escaping corruption.
- One file fully finished and validated before starting the next; never leave a file partially translated.
- Run at most 2-3 translation agents concurrently — more has tripped account usage limits with zero output produced.
- Default to the cheapest model for translation agents; escalate only where nuance clearly matters.
- Adjacent verses often share large stretches of commentary — check for byte-identical or near-identical source text between the current and previous verse before translating fresh (tag-swap reuse is standard practice here and saves significant work).
