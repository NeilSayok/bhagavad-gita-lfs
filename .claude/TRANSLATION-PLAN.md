# Bhagavad Gita — Multi-Language Translation Plan

Living plan for converting the `slok/` JSON dataset into a 4-language schema
(`hi`, `be`, `en`, `ka`) and translating all commentary by meaning.

Last updated: 2026-07-05

---

## 1. Goal & Scope

- **719 files** in `slok/` (`bhagavadgita_chapter_<C>_slok_<N>.json`).
- Convert user-facing fields into multi-language objects and translate the
  commentary of ~22 classical commentators into `hi` / `be` / `en` / `ka`.
- **Internal fields left untouched:** `_id`, `chapter`, `verse`.
- The legacy top-level `transliteration` field is **kept as-is** (redundant with
  `slok.en`, but nothing depends on removing it).

### Languages
| key | language | source of truth |
|-----|----------|-----------------|
| `hi` | Hindi | original `ht`/`hc`, else translated by meaning |
| `en` | English | original `et`/`ec`, else translated by meaning |
| `be` | Bengali | translated by meaning (target) |
| `ka` | Kannada | translated by meaning (target) |
| `sa` | Sanskrit | original `sc`, **preserved, never generated** |

---

## 2. Target Schema

### `speaker` and `slok` — transliteration only (NOT meaning translation)
```json
"speaker": { "hi": "धृतराष्ट्र", "be": "ধৃতরাষ্ট্র", "en": "Dhritarashtra", "ka": "ಧೃತರಾಷ್ಟ್ರ" },
"slok":    { "hi": "<Devanagari>", "be": "<Bengali script>", "en": "<IAST romanization>", "ka": "<Kannada script>" }
```
- `speaker.en` = readable name (Dhritarashtra / Sri Bhagavan / Arjuna / Sanjaya),
  NOT diacritic IAST. Only 4 distinct speakers exist in the whole corpus.
- `slok` = the same Sanskrit verse rendered script-for-script (transliteration),
  `en` reuses the existing `transliteration` field.

### Each commentator block
```json
"tej": {
  "author": "Swami Tejomayananda",
  "commentary": { "hi": "...", "en": "...", "be": "...", "ka": "...", "sa": "..." }
}
```
- Key order inside `commentary`: **hi, en, be, ka, (sa last if present)**.
- `sa` appears only on blocks that originally had Sanskrit commentary (`sc`).
- Explanations are translated **BY MEANING** (faithful natural prose), never 1:1.

### Original field → language-slot mapping (used during restructure)
`ht`, `hc` → `hi` &nbsp;|&nbsp; `et`, `ec` → `en` &nbsp;|&nbsp; `sc` → `sa`
(when two same-language fields exist, e.g. `ht`+`hc`, they are joined with `\n\n`).

---

## 3. Confirmed Decisions (from the user)

1. Convert `speaker` + `slok` (transliteration; do **not** translate the speaker's name).
2. Fill **all 4 keys** (`hi`, `be`, `en`, `ka`) for every field.
3. Hindi key is **`hi`** everywhere (an early draft used `hn`; normalized to `hi`).
4. Commentator text goes under **`commentary`** (an early draft used `meaning`; migrated).
5. **Keep `sa`** — preserve the authentic Sanskrit source; do not drop it.
6. Rollout order: **finish Chapter 1 first** (all 4 languages, all 47 verses),
   then continue chapter by chapter.
7. Use an **orchestrator + parallel sub-agent** workflow for scale (see §6).

---

## 4. Commentator Inventory (per file)

22 commentator keys (23rd, `prabhu`, present in 700/719 files):
`tej, siva, purohit, chinmay, san, adi, gambir, madhav, anand, rams, raman,
abhinav, sankar, jaya, vallabh, ms, srid, dhan, venkat, puru, neel, prabhu`.

Source-field shapes observed:
- Hindi-only (`ht` and/or `hc`): tej, chinmay, rams
- English-only (`et` and/or `ec`): purohit, san, adi, gambir, siva, prabhu
- Sanskrit-only (`sc` → `sa`): madhav, anand, jaya, vallabh, ms, srid, dhan, venkat, puru, neel
- Mixed: abhinav (et+sc), raman (et+sc), sankar (ht+et+sc)

Corpus text-field counts: `sc` 9 347, `et` 6 452, `ht` 2 157, `hc` 1 438, `ec` 1 419.
Total empty target slots to fill across all 719 files ≈ **53 000**.

---

## 5. Phases

### Phase 1 — Restructure (DONE, all 719 files)
- `speaker` + `slok` fully transliterated using the `indic-transliteration`
  Python lib (`sanscript`: DEVANAGARI → BENGALI / KANNADA / IAST).
- Every commentator block converted to `{author, commentary{hi,en,be,ka(,sa)}}`
  with original text in its source-language slot and empty `""` targets.
- Verified: valid JSON, **zero data loss** (all 20 812 original text fields retained).

### Phase 2 — By-meaning translation (IN PROGRESS)
- Chapter 1, **verse 1: 100% complete** (all 22 commentaries, all 4 languages) —
  serves as the **style/terminology reference** for every sub-agent.
- Chapter 1, verses 2–47: pending (≈ 3 300 empty slots).
- Remaining chapters (2–18): pending.

---

## 6. Agent Orchestration Workflow

**Model:** orchestrator (this main session) coordinates; **sub-agents** do the
translating and write directly to their assigned files.

### 6.1 Chunking
- Chunk by **verse** (each slok file is fully independent → no merge conflicts).
- Assign a contiguous **verse range per sub-agent** (~7–8 verses each).
- No two agents ever touch the same file.

### 6.2 Model routing
- Default **haiku** (cheapest, lowest quota pressure).
- Escalate to **sonnet** only where nuance clearly matters.
- **Run 2–3 agents at a time (sequential batches)**, not 6 in parallel —
  6 parallel sonnet agents tripped the account usage limit and produced nothing.

### 6.3 Per-agent contract (prompt must include)
1. Read `slok/bhagavadgita_chapter_1_slok_1.json` as the style reference.
2. Explicit file list (only those files).
3. Fill every empty `hi/en/be/ka` slot BY MEANING from the populated source
   (`hi`/`en`, else `sa`). Never modify filled slots, `author`, `sa`, or the
   internal/verse/speaker/slok fields. Preserve key order.
4. Native-digit verse markers (e.g. `১.২০`, `೧.೨೦`).
5. Shared **consistency glossary** (see §7).
6. **Write via Python** (`json.load` → fill → `json.dump(ensure_ascii=False, indent=4)`
   → trailing newline), then re-parse to confirm validity + no empty slots.
7. **CRITICAL: do the work yourself — do NOT spawn/delegate to another sub-agent.**
8. Reply with a short summary only (never paste translations back — saves tokens).

### 6.4 Compile & review (orchestrator, after each batch)
- **Never trust the "completed" status** — verify the actual files:
  - every file parses as JSON;
  - **zero** empty `hi/en/be/ka` slots in the batch's verses;
  - spot-check terminology vs the glossary and verse 1.
- Re-dispatch any verse that came back empty/partial.
- Only advance to the next batch once the current one verifies clean.

### 6.5 Chapter-1 batch map
| batch | agent verses |
|-------|--------------|
| 1 | 2–9, 10–17, 18–25 |
| 2 | 26–33, 34–40, 41–47 |

---

## 7. Consistency Glossary (Bengali / Kannada)

```
Kurukshetra   কুরুক্ষেত্র / ಕುರುಕ್ಷೇತ್ರ      dharmakshetra ধর্মক্ষেত্র / ಧರ್ಮಕ್ಷೇತ್ರ
Arjuna        অর্জুন / ಅರ್ಜುನ              Krishna       শ্রীকৃষ্ণ / ಶ್ರೀಕೃಷ್ಣ
Dhritarashtra ধৃতরাষ্ট্র / ಧೃತರಾಷ್ಟ್ರ        Sanjaya       সঞ্জয় / ಸಂಜಯ
Bhishma       ভীষ্ম / ಭೀಷ್ಮ                Drona         দ্রোণ / ದ್ರೋಣ
Duryodhana    দুর্যোধন / ದುರ್ಯೋಧನ          Yudhishthira  যুধিষ্ঠির / ಯುಧಿಷ್ಠಿರ
Pandavas      পাণ্ডবেরা / ಪಾಂಡವರು          Kauravas      কৌরবেরা / ಕೌರವರು
Hrishikesha   হৃষীকেশ / ಹೃಷೀಕೇಶ           Gandiva       গাণ্ডীব / ಗಾಂಡೀವ
dharma        ধর্ম / ಧರ್ಮ                  adharma       অধর্ম / ಅಧರ್ಮ
```
Transliterate any other Sanskrit name/term into the target script consistently.

---

## 8. Issues Encountered & Mitigations

| Issue | Effect | Mitigation |
|-------|--------|------------|
| **Account usage/session limit** | Parallel sonnet agents killed with tiny token counts, 0 output | Fewer agents (2–3), route to **haiku**, run in sequential batches; retry after the stated reset time |
| **Agents delegate** instead of translating | General-purpose agent spawns a child agent, burns tokens, no file changes | Prompt must say **"do the work yourself; do NOT spawn any sub-agent"** |
| **"completed" status lies** | Status says done while files are unchanged | Always verify actual files (JSON valid + 0 empty slots) before trusting |
| Manual JSON string edits risk escaping errors | Broken Unicode/JSON | Agents must edit via Python `json` with `ensure_ascii=False` |

### Reliable fallback
If the sub-agent route keeps returning empty (limits/delegation), the orchestrator
translates directly in the main session, one verse per turn (this is how verse 1
was completed). Slower and heavier on main-session tokens, but deterministic.

---

## 9. Progress Tracker

- [x] Phase 1 restructure — all 719 files
- [x] Ch1 v1 — complete (reference verse)
- [x] Ch1 v2 — complete (all 22 blocks, 4 langs; done in main session)
- [ ] Ch1 v3–47 — pending
- [ ] Ch2–Ch18 — pending

### Reuse optimization (discovered while doing v2)
Some Sanskrit blocks are the **same continuous commentary duplicated across
consecutive verse records**, differing only in the leading verse tag:
- `venkat` (~3286 ch) and `raman` (~1133 ch): **99.9% identical across v2–v9**
  (only the `।।1.N।।` marker changes). Translate once → reuse, swapping the tag.
- `abhinav` (85 ch) and `vallabh` (200 ch): **byte-identical** across v3,v4,v6,v7,v9
  (= v2), with a second identical variant on v5,v8. v10 differs (real aparyaptam gloss).
- `madhav`/`jaya`: short "did not comment on this sloka; commentary starts 2.11"
  placeholders — same boilerplate, just the verse number changes.
- Genuinely per-verse (must translate individually): siva, purohit, san, adi,
  gambir, prabhu (English source) + anand, ms, srid, dhan, puru, neel (Sanskrit).
This turns v3–v9 into mostly the per-verse blocks + tag-swapped reuse.

### Pace reality
At faithful by-meaning fidelity this is ~1 verse per turn in the main session
(v2 alone: venkat = 3286 ch Sanskrit × 4 langs). Full Ch1 is a multi-session
effort; continue verse-by-verse, verifying 0 empty slots after each.

Quick status check:
```bash
python3 - <<'PY'
import json,glob
e=t=0
for f in glob.glob('slok/*.json'):
    d=json.load(open(f))
    for k,v in d.items():
        if isinstance(v,dict) and 'commentary' in v:
            for l in ('hi','en','be','ka'):
                if v['commentary'].get(l,'').strip(): t+=1
                else: e+=1; t+=1
print(f"empty {e} / total {t}")
PY
```

---

## 10. Environment Notes

- Repo path contains a space: `/Users/neil/AndroidStudioProjects/Gita/V1/DB/bhagavad-gita copy`.
- `indic-transliteration` is installed (used for Phase 1 script conversion).
- No translation API is available in-environment — meaning-translation is produced
  by the LLM (sub-agents or main session), not a service.
