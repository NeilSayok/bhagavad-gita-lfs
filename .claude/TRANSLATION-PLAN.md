# Bhagavad Gita — Multi-Language Translation Plan

Living plan for converting the `slok/` JSON dataset into a multi-language schema
(`hi`, `en`, `be`, `ka`, with `sa` preserved) and translating all commentary
**by meaning**, using dedicated Claude Code sub-agents.

Last updated: 2026-07-05

---

## 1. Goal & Scope

Translate the Bhagavad Gita repository into multiple languages while preserving:

- Philosophical accuracy
- Spiritual meaning
- Consistent terminology across the entire corpus
- Natural, native-sounding language
- JSON integrity

Concretely:

- **719 files** in `slok/` (`bhagavadgita_chapter_<C>_slok_<N>.json`), each a
  single verse and an **independent unit of work**.
- Convert user-facing fields into multi-language objects and translate the
  commentary of ~22 classical commentators into `hi` / `en` / `be` / `ka`.
- **Internal fields left untouched:** `_id`, `chapter`, `verse`.
- The legacy top-level `transliteration` field is **kept as-is** (redundant with
  `slok.en`, but nothing depends on removing it).

### Languages
| key | language | agent | source of truth |
|-----|----------|-------|-----------------|
| `hi` | Hindi | `hi-translation-agent.md` | original `ht`/`hc`, else translated by meaning |
| `en` | English | `en-translation-agent.md` | original `et`/`ec`, else translated by meaning |
| `be` | Bengali | `be-translation-agent.md` | translated by meaning (target) |
| `ka` | Kannada | `ka-translation-agent.md` | translated by meaning (target) |
| `sa` | Sanskrit | `sa-translation-agent.md` | original `sc`, **preserved, never generated** |

All agent definitions live inside `.claude/agents/`.

> **On Sanskrit (`sa`):** Sanskrit is the canonical **source of truth**, not a
> generation target. `sa` appears only on blocks that originally had Sanskrit
> commentary (`sc`) and is **never invented or back-translated**. The
> `sa-translation-agent` exists only to **preserve/validate** existing Sanskrit
> (verify it is intact and correctly slotted) — it does not create new Sanskrit.

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
2. Fill **all 4 target keys** (`hi`, `be`, `en`, `ka`) for every field.
3. Hindi key is **`hi`** everywhere (an early draft used `hn`; normalized to `hi`).
4. Commentator text goes under **`commentary`** (an early draft used `meaning`; migrated).
5. **Keep `sa`** — preserve the authentic Sanskrit source; do not drop or generate it.
6. Rollout order: **finish Chapter 1 first** (all 4 languages, all 47 verses),
   then continue chapter by chapter.
7. Use an **orchestrator + dedicated per-language sub-agent** workflow (see §6).

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
- Chapter 1, verses 2–47: in progress (≈ 3 300 empty slots).
- Remaining chapters (2–18): pending.

---

## 6. Agent Orchestration Workflow

**Architecture: Orchestrator → dedicated language agent.** The orchestrator
(this main session) coordinates; each language has **exactly one dedicated agent**
that translates **only its own language** and writes directly to the assigned file.

```
                    Orchestrator
                         │
        ┌────────┬────────┬────────┬────────┐
        ▼        ▼        ▼        ▼        ▼
      Hindi   English  Bengali  Kannada  Sanskrit
      Agent    Agent    Agent    Agent    Agent
                                        (preserve/validate only)
```

An agent never translates into any other language.

### 6.1 Unit of work — file-based (replaces verse-range batching)
- The unit of work is **one whole JSON file** (one verse), not a verse range.
- Each slok file is fully independent → no merge conflicts.
- **One file is finished, saved, and validated before the next is assigned.**
  The next file is never started before the current one is complete.
- No two agents ever touch the same file at the same time.

### 6.2 Per-file loop
1. Orchestrator selects a file, e.g. `slok/bhagavadgita_chapter_2_slok_47.json`.
2. Orchestrator invokes the appropriate language agent for that file.
3. The agent: reads the complete JSON → fills every empty slot for **its** language
   BY MEANING → saves → validates → reports completion.
4. Orchestrator verifies the file, then assigns the next one.

A language agent must always: process exactly one file, finish the entire file,
save, validate, report success, then wait. Never process multiple files at once;
never leave a file partially translated.

### 6.3 Model routing & concurrency
- Default **haiku** (cheapest, lowest quota pressure); escalate to **sonnet**
  only where nuance clearly matters.
- **Run at most 2–3 agents concurrently, in sequential batches** — 6 parallel
  sonnet agents tripped the account usage limit and produced nothing (see §8).

### 6.4 Per-agent contract (prompt must include)
1. Read `slok/bhagavadgita_chapter_1_slok_1.json` as the style/terminology reference.
2. The single assigned file (only that file).
3. Fill every empty slot **for the agent's assigned language only**, BY MEANING,
   from the populated source (`hi`/`en`, else `sa`). Never modify filled slots,
   `author`, `sa`, other languages, or the internal/`chapter`/`verse`/`speaker`/`slok`
   fields. Preserve key order (hi, en, be, ka, sa-last).
4. Native-digit verse markers (e.g. `১.২০`, `೧.೨೦`).
5. Shared **consistency glossary** (see §7).
6. **Write via Python** (`json.load` → fill → `json.dump(ensure_ascii=False, indent=4)`
   → trailing newline), then re-parse to confirm validity + no empty slots.
7. **CRITICAL: do the work yourself — do NOT spawn/delegate to another sub-agent.**
8. Reply with a short summary only (never paste translations back — saves tokens).

### 6.5 Compile & review (orchestrator, after each file / batch)
- **Never trust the "completed" status** — verify the actual file:
  - it parses as JSON;
  - **zero** empty slots for the language(s) just processed;
  - spot-check terminology vs the glossary and verse 1.
- Re-dispatch any file that came back empty/partial (see §9 failure recovery).
- Only advance once the current file verifies clean.

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

## 9. Failure Recovery

If validation fails for a file:

1. Discard the result.
2. Reassign the **same** file to its language agent.
3. Re-run the agent.
4. Validate again.

Never continue to the next file until the current one passes validation.

---

## 10. Progress Tracking

Progress is tracked **independently per language** so work can resume safely at
any point:

```
Hindi     ✓ 1-1  ✓ 1-2  ✓ 1-3  ...
English   ✓ 1-1  ✓ 1-2  ...
Bengali   ✓ 1-1  ...
Kannada   ✓ 1-1  ...
```

### Current status
- [x] Phase 1 restructure — all 719 files
- [x] Ch1 v1 — complete (reference verse; verified genuinely translated)
- [x] Ch1 v2 — complete (all 22 blocks, 4 langs) — **re-fixed 2026-07-05**: 14 slots
  had been bogus (en placeholder `[Translation of …]`, be/ka were Hindi copies);
  now real by-meaning en/be/ka incl. full `rams` vyakhya. Verified 0 empty, 0 bogus.
- [x] Ch1 v3 — complete (2026-07-05): all 22 blocks ×4 langs. Reused v2 for
  venkat/raman/madhav/jaya (tag-swap 1.2→1.3) + abhinav/vallabh (range markers, verbatim);
  genuine by-meaning for tej/chinmay/siva/purohit/san/adi/gambir/prabhu/anand/srid/puru/neel/ms/dhan/rams
  + sankar be/ka fix. Verified 0 empty, 0 bogus.
- [x] Ch1 v4 — complete (2026-07-05): all 22 blocks ×4 langs (warriors list; rams 1.4-1.6,
  ms with maharatha/atiratha definition, dhan 1.4-1.5). Reuse venkat/raman/madhav/jaya from
  v3 (tag-swap 1.3→1.4) + abhinav/vallabh verbatim; ms/dhan/srid/anand/puru/neel are per-verse
  DISTINCT (not reusable). Verified 0 empty, 0 bogus, sa preserved (13 blocks).
- [x] Ch1 v5 — complete (2026-07-05): 0 empty/bogus. Reused venkat/raman/madhav/jaya/ms/puru
  from v4 (tag/whitespace-only diffs) + abhinav/vallabh/dhan verbatim; rams = full 1.4-1.6
  (v4 base + kashiraja→sarva-maharathah continuation); anand/srid/neel short new blocks.
- [x] Ch1 v6 — complete (2026-07-05): 0 empty/bogus. Reused venkat/raman/madhav/jaya/ms (tag-swap)
  + abhinav/vallabh + rams (full 1.4-1.6 verbatim from v5); chinmay now REAL commentary; puru/dhan/anand/srid/neel new.
- [x] Ch1 v7 — complete (2026-07-06): 0 empty/bogus. File was mostly pre-filled; the 6
  Sanskrit-source blocks anand/ms/srid/dhan/puru/neel were empty and got genuine by-meaning
  hi/en/be/ka (Duryodhana names his own chief warriors to Drona; ms has the full roster gloss
  Ashvatthama/Vikarna/Saumadatti-Bhurishrava/Jayadratha + shalya/kritavarma tyaktajivita).
- [x] Ch1 v8 — complete (2026-07-06): 0 empty/bogus. Commit 4b27ed5 had only PARTLY filled it —
  64 empty + 8 bogus (be/ka Hindi-copies) + tej/chinmay/rams .en were `[Translation of …]`
  placeholders. Full verse: reused raman/madhav/jaya (tag-swap) + abhinav/vallabh (verbatim) +
  ms (identical to v7, verbatim) from prior verses; venkat = the long aparyaptam(1.10) grammatical
  analysis (4 readings) translated fresh; anand/srid/dhan/puru/neel + 6 English-src blocks + sankar
  did-not-comment boilerplate all genuine. **Lesson: commit 4b27ed5's "v8,v9" were NOT complete.**
- [x] Ch1 v9 — complete (2026-07-06): 0 empty/bogus. Was partly pre-filled by 4b27ed5 (64 empty
  + 8 bogus be/ka Hindi-copies + tej/chinmay/rams .en `[Translation…]` placeholders + sankar.hi
  English placeholder). Reused madhav/jaya/raman/ms/venkat from v8 (1.8→1.9 tag-swap; verified no
  collateral digit collisions — venkat body refs 18.78/1.10/1.11 untouched) + abhinav/vallabh
  verbatim; anand/srid/dhan/puru/neel (the "anye ca / madarthe / nana / sarve" gloss) + 6 English-src
  + sankar boilerplate all genuine.
- [ ] Ch1 v10–48 — pending. **v10 differs: real aparyaptam gloss (abhinav/vallabh NOT verbatim
  reuse per §10 note); expect distinct sa blocks.**
- [ ] Ch2–Ch18 — pending

### Reuse identity check (use whitespace-normalized!)
Source `sa` blocks differ across verses only by leading tag + OCR whitespace/typos. Compare with
`re.sub(r'\s+','', strip_leading_tag(s))` — raw `==` gives false negatives. venkat/raman/madhav/jaya/ms/puru
repeat (tag-swap); abhinav/vallabh/dhan are range-marker blocks (verbatim). Always confirm per verse.

### v4→ reuse note
Only venkat/raman/madhav/jaya (+abhinav/vallabh ranges) repeat across verses. The other
Sanskrit blocks (ms, dhan, srid, anand, puru, neel) and all English/Hindi-source blocks are
genuinely per-verse — must be translated fresh each verse. Stage scripts in scratchpad:
v{N}_A..F.py (A=reuse+tej+chinmay+sankar, B=english-src, C=rams, D=anand/srid/puru/neel, E=ms, F=dhan).

### Reuse-swap gotcha (learned v3)
`abhinav` and `vallabh` markers are RANGES (`।।1.2  1.9।।`, `।।1.2  1.11।।`) that
cover verses 2–9 / 2–11 — they do NOT change per verse. Only swap the leading tag for
venkat/raman/madhav/jaya. Reuse helper in scratchpad `v3_A.py` (`swap_lead`); it wrongly
hit abhinav's `१.२` once — exclude range-marker blocks from swapping.

### Bogus-slot detector (empty-counter is NOT enough)
The `.strip()`-empty check counts wrong-language copies and `[Translation …]`
placeholders as "done". Real verification must also flag: `en` starting with
`[Translation`, and `be`/`ka` containing Devanagari without any Bengali/Kannada
script. Run this after every file:
```bash
python3 - <<'PY'
import json,glob,re
dev=re.compile(r'[ऀ-ॿ]'); beng=re.compile(r'[ঀ-৿]'); kan=re.compile(r'[ಀ-೿]')
for f in sorted(glob.glob('slok/bhagavadgita_chapter_1_slok_*.json')):
    d=json.load(open(f)); bad=[]; empt=0
    for k,v in d.items():
        if isinstance(v,dict) and 'commentary' in v:
            c=v['commentary']
            for l in ('hi','en','be','ka'):
                if not c.get(l,'').strip(): empt+=1
            if c.get('en','').strip().startswith('[Translation'): bad.append(k+'.en')
            be=c.get('be','').strip(); ka=c.get('ka','').strip()
            if be and dev.search(be) and not beng.search(be): bad.append(k+'.be')
            if ka and dev.search(ka) and not kan.search(ka): bad.append(k+'.ka')
    print(f, 'empty',empt,'bogus',len(bad),bad[:6])
PY
```

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

## 11. Design Principles

- One language = one dedicated agent.
- One file = one unit of work.
- Finish the current file before starting the next.
- Never delegate translation (agents do the work themselves).
- Translate **by meaning**, never word-for-word; no added commentary/summary.
- Sanskrit (`sa`) is the canonical source — preserved, never generated.
- Preserve JSON integrity (valid JSON, Unicode, key order, formatting).
- Maintain terminology consistency across the entire corpus.

---

## 12. Environment Notes

- Repo path contains a space: `/Users/neil/AndroidStudioProjects/Gita/V1/DB/bhagavad-gita copy`.
- `indic-transliteration` is installed (used for Phase 1 script conversion).
- No translation API is available in-environment — meaning-translation is produced
  by the LLM (sub-agents or main session), not a service.
