# Bhagavad Gita — Multi-Language Translation Plan

Living plan for converting the `slok/` JSON dataset into a multi-language schema
(`hi`, `en`, `be`, `ka`, with `sa` preserved) and translating all commentary
**by meaning**, using dedicated Claude Code sub-agents.

Last updated: 2026-07-05

---

### Start from chapter 18 then go to 17 then 16, etc. (reverse order)

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
- [x] Ch1 v10 — complete (2026-07-09): 0 empty/bogus. Duryodhana's aparyaptam/paryaptam verse.
  siva/san had leftover v1 garbage in .hi (fixed); 12 bogus be/ka slots (Hindi copies) across
  siva/chinmay/san/adi/gambir/sankar fixed. vallabh reused v9 verbatim (sa identical); madhav/jaya
  reused v9 tag-swapped (1.9→1.10). venkat = fresh, full 4-reading grammatical exegesis
  (pathabheda/vyavahitanvaya/vakyabheda/padarthabheda) of the aparyaptam ambiguity + defense of
  why Bhima is named opposite Bhishma — longest block this verse (~3288 ch sa). anand/ms/srid/
  dhan/puru/neel/raman/sankar/abhinav all fresh per-verse content; 6 English-src blocks
  (siva/purohit/san/adi/gambir/prabhu) genuine. madhav/jaya/vallabh .en tag-swapped from v9.
- [x] Ch1 v11 — complete (2026-07-09): 0 empty/bogus. "Protect Bhishma alone" verse. Reused
  raman.en/madhav/jaya (tag-swap 1.10→1.11) + vallabh (range 1.2–1.11 verbatim, unchanged) from
  v10; venkat's sa is a running commentary whose first ~3288 ch are byte-identical to v10 (only
  tag differs) plus ~750 ch of fresh continuation (defending that verse 1.10's reasoning wasn't
  actually unstated) — reused v10's translation for the shared part + freshly translated the
  continuation. anand/ms/srid/dhan/puru/neel/raman.hi-be-ka/abhinav/sankar-be-ka + 6 English-src
  + tej/chinmay/rams/prabhu all fresh by-meaning. **Caught own bug**: a stray trailing comma in
  the anand fill script silently turned 3 string fields into 1-element JSON lists (json.dump
  serializes tuples as arrays) — detector didn't catch it since non-empty; only found via
  explicit `isinstance(v, dict)`/type check. Added a `nonstr` check to the detector for future
  verses — always verify field types are `str`, not just non-empty.
- [x] Ch1 v12 — complete (2026-07-10): 0 empty/bogus, 0 nonstr. Bhishma roars/blows conch to
  cheer Duryodhana. Reused raman.en/madhav/jaya (tag-swap 1.11→1.12) from v11; abhinav flips to
  "no commentary" boilerplate (range 1.12-1.29, distinct from prior verbatim-gloss pattern);
  vallabh is a fresh range block (1.12-1.13, not reusable from v11's 1.2-1.11 range). venkat's sa
  is a fully distinct new commentary (not a continuation this time) — defends the harsha/vishada
  word-order logic of the verse against several objections, then closes with grammar notes on
  tasya sanjanayan...krtva...akarayat; translated fresh in full (~3276 ch). anand/ms/srid/dhan/
  puru/neel/raman.hi-be-ka/sankar-be-ka + 6 English-src + tej/chinmay/rams/prabhu fresh.
- [x] Ch1 v13 — complete (2026-07-10): 0 empty/bogus/nonstr. Conches/kettledrums answer Bhishma's
  roar. venkat's sa was byte-identical (tag-swapped) to the closing grammar-note half of v12's
  venkat block — reused that translated portion directly instead of re-translating. Reused
  raman.en-pattern via madhav/jaya tag-swap, vallabh verbatim (range 1.12-1.13 unchanged), abhinav
  boilerplate tag-swap. anand/ms/srid/dhan/puru/neel/raman.hi-be-ka/sankar-be-ka + 6 English-src +
  tej/chinmay/rams/prabhu fresh (prabhu has no purport paragraph this verse, translation-only).
- [x] Ch1 v14 — complete (2026-07-10): 0 empty/bogus/nonstr. Krishna and Arjuna answer with
  divine conches from their white-horsed chariot. Reused raman.hi-be-ka-pattern via madhav/jaya/
  abhinav tag-swap (1.13→1.14); vallabh and venkat both fresh per-verse blocks this time (no
  carry-over text). anand/ms/srid/dhan/puru/neel/raman.hi-be-ka/sankar-be-ka + 6 English-src +
  tej/chinmay/rams/prabhu fresh — rams has a long etymological note on Arjuna's 100 divine
  horses (gift of Chitraratha) and the Agni-given chariot (Khandava-dahana backstory).
- [x] Ch1 v15 — complete (2026-07-10): 0 empty/bogus/nonstr. Krishna blows Panchajanya, Arjuna
  Devadatta, Bhima the great conch Paundra (etymologies: Bhimakarma/Vrikodara, Dhananjaya,
  Hrishikesha). Reused raman.hi-be-ka-pattern via madhav/jaya/abhinav tag-swap (1.14→1.15);
  vallabh now a fresh range block (1.15-1.19, previewing the whole Pandava conch sequence).
  anand/ms/srid/dhan/puru/neel/raman.hi-be-ka/sankar-be-ka + 6 English-src + tej/chinmay/rams/
  prabhu fresh — rams has conch-name etymologies (Panchajanya demon, Devadatta from Indra,
  Vrikodara's digestive fire), prabhu explains Krishna's name variants (Madhusudana, Govinda, etc).
- [x] Ch1 v16 — complete (2026-07-10): 0 empty/bogus/nonstr. Yudhishthira blows Anantavijaya,
  Nakula/Sahadeva blow Sughosha/Manipushpaka. High reuse verse: ms and venkat sa were byte-for-byte
  identical to v15's (just tag/whitespace), reused verbatim; vallabh unchanged (range 1.15-1.19);
  madhav/jaya/abhinav tag-swapped as usual. chinmay = "No commentary" this verse. anand/srid/dhan/
  puru/neel/raman.hi-be-ka/sankar-be-ka + 6 English-src + tej/rams/prabhu fresh — rams explains
  Kunti-sons vs Madri-sons distinction and Yudhishthira's "raja" epithet foreshadowing kingship.
- [x] Ch1 v17 — complete (2026-07-10): 0 empty/bogus/nonstr. King of Kashi, Shikhandi,
  Dhrishtadyumna, Virata, Satyaki named. High reuse: ms/venkat/vallabh sa byte-identical to v16's
  (verbatim reuse), madhav/jaya/abhinav tag-swapped. rams covers 1.17-1.18 together with the
  Shikhandi backstory (former life as Amba, sex-change via Sthunakarna yaksha, why Bhishma
  wouldn't fight him) and Abhimanyu's chakravyuha death — plus a note that Sanjaya's asymmetric
  naming (18 Pandava heroes vs only Bhishma on Kaurava side) reveals his sympathies.
  anand/srid/dhan/puru/neel/raman.hi-be-ka/sankar-be-ka + 6 English-src + tej/chinmay/prabhu fresh.
- [x] Ch1 v18 — complete (2026-07-10): 0 empty/bogus/nonstr. Drupada, Draupadi's five sons,
  Abhimanyu blow conches. Very high reuse: ms/venkat/vallabh identical to v17; madhav/jaya/
  abhinav/puru all tag-swap reusable (puru's sa turned out identical too, unusual — worth
  checking puru each verse in this stretch); rams's block spans 1.17-1.18 (same text as v17,
  reused en/be/ka directly, no retranslation needed). anand/srid/dhan/raman.hi-be-ka/sankar-be-ka
  + 6 English-src + tej/chinmay/prabhu fresh.
- [x] Ch1 v19 — complete (2026-07-10): 0 empty/bogus/nonstr. Closes the conch-blowing sequence
  (v2-v19): the uproar rends the Kauravas' hearts. venkat/vallabh still byte-identical to v18
  (verbatim reuse); madhav/jaya/abhinav tag-swapped. rams has a long dharma/adharma digression
  (why the Kaurava conches had no effect on the Pandavas but vice versa did — righteous hearts
  are unshaken; Ravana fearful despite universal dread of him) + the chapter-structural note that
  Sanjaya's answer to "what did my sons and Pandu's sons do" (asked in v1) spans v2-v19, and v20
  begins the actual Gita narrative proper. anand/ms/srid/dhan/puru/neel/raman.hi-be-ka/sankar-be-ka
  + 6 English-src + tej/chinmay/prabhu fresh.
- [x] Ch1 v20 — complete (2026-07-10): 0 empty/bogus/nonstr. Arjuna sees the armies arrayed and
  raises his Gandiva bow. First verse after the conch sequence ends — high-reuse streak broken;
  raman/venkat/ms/vallabh all fresh content this verse (raman.en dropped from the 1890-char range
  narrative to a short 225-char verse-specific reply). rams explains "atha" marking the start of
  the Gita dialogue proper (spans 2.11-18.66), the Hanuman-banner backstory (boon granted to
  Bhima in the Kadali forest), and contrasts Duryodhana's fear (ran to Drona) vs Arjuna's
  fearlessness (reached straight for his bow). madhav/jaya/abhinav/sankar-be-ka still tag-swap
  reusable. anand/ms/srid/dhan/puru/neel/raman/vallabh + 6 English-src + tej/chinmay/prabhu fresh.
- [x] Ch1 v21 — complete (2026-07-10): 0 empty/bogus/nonstr. Arjuna's first words: "station my
  chariot between the two armies, O Achyuta." Reuse resumed here: raman/madhav/jaya/abhinav/
  vallabh/ms/venkat/puru all byte-identical to v20 (tag-swap only) since 1.20-1.21 form one
  continuous sentence in the source and several commentators treat them as a single unit; anand/
  dhan/srid/neel/rams/6-English-src/tej/chinmay/prabhu fresh. rams explains the "between the two
  armies" phrase's threefold recurrence in the Gita (1.21, 1.24, 2.10) as marking Arjuna's arc
  from valor to delusion to receiving Krishna's teaching.
- [x] Ch1 v22 — complete (2026-07-10): 0 empty/bogus/nonstr. Arjuna continues: "so I may see who
  I must fight." rams and prabhu's purport were byte-identical/near-identical to v21's (rams full
  reuse of en/be/ka; prabhu purport paragraph reused, only the verse-translation line retranslated
  fresh). madhav/jaya/abhinav/raman/vallabh/venkat tag-swap reusable. anand/ms/srid/dhan/puru/neel
  + 6 English-src + tej/chinmay fresh.
- [x] Ch1 v23 — complete (2026-07-10): 0 empty/bogus/nonstr. Arjuna finishes: "let me see who
  wishes to please the ill-minded Duryodhana in this war." san's en block spans 1.23-1.24 together
  (Sanjaya's narration + "behold these Kurus" — translated as one unit matching source). venkat's
  sa was v22's text plus a short fresh continuation tail — reused v22's translation and appended a
  fresh rendering of just the new part (same technique as v12→v13, v20→v21 continuations).
  madhav/jaya/abhinav/raman/vallabh tag-swap reusable. anand/ms/srid/dhan/puru/neel + 6
  English-src + tej/chinmay/prabhu fresh; rams has a strong dharma-critique passage (the assembled
  kings should have counseled Duryodhana toward justice, not war).
- [x] Ch1 v24 — complete (2026-07-10): 0 empty/bogus/nonstr. Sanjaya narrates: Krishna stations
  the chariot between the armies, facing Bhishma/Drona/all kings. **Lesson repeated**: when
  reusing a multi-verse-spanning block (san's en here matched v23's exactly), remember to copy
  hi/be/ka too, not just en — first pass missed san.hi/be/ka, caught by detector, fixed by
  reusing v23's san hi/be/ka (also spans 1.23-1.24). vallabh now fresh (new range 1.24-1.25).
  madhav/jaya/abhinav/raman tag-swap. anand/ms/srid/dhan/puru/neel/venkat + tej/chinmay/prabhu
  fresh; rams (spanning 1.24-1.25) has a rich passage on why Krishna said "behold these Kurus"
  (not "Dhritarashtra's men") — deliberately awakening Arjuna's kinship-delusion as the doctor
  lances a ripened boil, since only through that delusion could the Gita's teaching arise; plus
  a comparison of familial affection vs. love of God (moha vs. atmiyata, darkness vs. light).
- [x] Ch1 v25 — complete (2026-07-10): 0 empty/bogus/nonstr. Krishna: "behold these Kurus
  assembled." Very high reuse verse: madhav/jaya/abhinav/raman/vallabh/ms/dhan all byte-identical
  to v24 (tag-swap); adi/gambir/rams reused v24's translation verbatim (same content spans
  1.24-1.25); venkat's sa was an exact substring of v24's venkat body — sliced the matching
  portion out of v24's already-translated text instead of retranslating. anand/srid/puru/neel +
  tej/chinmay/prabhu fresh; san's source text here oddly describes verse-26-ish content (fathers,
  grandfathers, teachers) rather than "behold" — translated faithfully as given (a known upstream
  data quirk, not something to "fix").
- [x] Ch1 v26 — complete (2026-07-10): 0 empty/bogus/nonstr. Arjuna sees fathers, grandfathers,
  teachers, uncles, brothers, sons, grandsons, friends in both armies. venkat is a long
  chapter-summary block previewing verses 27-37 (aggressor/atatayin doctrine, Manu citations,
  "mayaivaite nihatah" 11.33 foreshadowing) — translated in full. madhav/jaya/abhinav tag-swap;
  raman and vallabh both fresh (new content/range). anand/ms/srid/dhan/puru/neel + 6 English-src +
  tej/chinmay/prabhu fresh; rams has the full named-relative roster (Bhurishrava, Bhishma,
  Somadatta, Drona, Kripa, Shalya, Shakuni, Duryodhana, Abhimanyu, Lakshmana, Ashvatthama,
  Drupada, Satyaki, Kritavarma).
- [x] Ch1 v27 — complete (2026-07-10): 0 empty/bogus/nonstr. Arjuna overcome with compassion,
  becomes despondent. Very high reuse: madhav/jaya/abhinav/raman/vallabh/venkat/ms all
  byte-identical to v26 (tag-swap) — venkat's ~2637-char chapter-summary block carries over
  unchanged since it previews multiple verses at once. chinmay has a long, notably skeptical
  psychological analysis calling Arjuna's "compassion" a euphemism for a collapse of
  self-control/nerve, not genuine dharmic compassion (an unusually critical reading vs. other
  commentators). anand/srid/dhan/puru/neel + 6 English-src + tej/rams/prabhu fresh; prabhu has
  no purport paragraph this verse (translation-only, per source).
- [x] Ch1 v28 — complete (2026-07-10): 0 empty/bogus/nonstr. Arjuna's grief speech begins:
  "seeing my own kinsmen eager for battle." venkat's ~2637-char summary block still identical
  (3rd verse running); madhav/jaya/abhinav/raman also tag-swap reusable. vallabh/ms broke reuse
  here (fresh, shorter — vallabh now a 1.28-1.30 range preview, ms genuinely new). rams explains
  the significance of "Krishna"/"Partha" as intimate mutual names (9 occurrences in the Gita) and
  contrasts Dhritarashtra's "mamakah/pandavah" divide with Arjuna's unifying "svajanam". chinmay
  gives a notably clinical psychological read again (naming Arjuna's state "anxiety-induced
  despair", not spiritual compassion). anand/srid/dhan/puru/neel + 6 English-src + tej/chinmay/
  prabhu fresh; prabhu has a long purport quoting Bhagavatam 5.18.12 on devotee qualities.
- [x] Ch1 v29 — complete (2026-07-10): 0 empty/bogus/nonstr (after fixing a trailing-comma bug
  in the prabhu fill that turned hi/be into 1-element lists — same recurring mistake as v12/v21;
  caught by the type check, not the empty check). Arjuna's bodily symptoms of grief: limbs
  failing, mouth drying, trembling, hair standing on end. Extremely high reuse: madhav/jaya/
  abhinav/raman/vallabh/venkat all byte-identical to v28 (tag-swap); chinmay and rams reused
  verbatim (same repeated content). anand/ms/srid/dhan/puru/neel + 6 English-src + tej/prabhu
  fresh. **Recurring gotcha**: when writing FILL dicts by hand across many verses, watch for
  stray trailing commas after a dict-value string — they silently create 1-tuples that json.dump
  serializes as arrays; always run the nonstr type-check, not just the empty-check.
- [x] Ch1 v30 — complete (2026-07-10): 0 empty/bogus/nonstr (again hit + fixed the prabhu
  trailing-comma bug — 4th occurrence, pattern now well-documented). Gandiva slips, skin burns,
  cannot stand, mind reeling. abhinav flips from boilerplate to a substantive philosophical
  preview spanning 1.30-1.34 (the "vishesha-buddhi" doctrine — killing conceived with an
  individualizing notion of who's being slain, or for personal gain, generates sin regardless;
  foreshadows Krishna's "perform action as pure duty" answer). madhav/jaya/vallabh/venkat
  tag-swap; raman/rams reused verbatim (identical repeated content). anand/ms/srid/dhan/puru/neel
  + 6 English-src + tej/chinmay/prabhu fresh.
- [x] Ch1 v31 — complete (2026-07-10): 0 empty/bogus/nonstr. "I see adverse omens, and no good
  in killing my kinsmen." venkat drops to "no commentary" boilerplate here (was the long v26-v30
  summary block); vallabh likewise boilerplate for range 1.31-1.33. madhav/jaya/abhinav tag-swap;
  raman reused verbatim. anand/ms/srid/dhan/puru/neel + 6 English-src + tej/chinmay/prabhu fresh;
  rams explains the two categories of omens (personal bodily symptoms + cosmic portents like
  meteors/eclipses/blood rain) both read as inauspicious.
- [x] Ch1 v32 — complete (2026-07-10): 0 empty/bogus/nonstr. "I do not desire victory, kingdom,
  or pleasures, O Krishna/Govinda." raman/madhav/jaya/abhinav/vallabh/venkat all byte-identical
  to v31 — tag-swap reuse. san.en content is actually v33's ("for whose sake we seek kingdom...
  stand arrayed to fight") — upstream verse-mismatch quirk, translated as-is per policy. neel.sa
  also stale/mismatched (v31's earthquake-omen content reused verbatim) — same policy applied,
  translated as-is rather than "fixed". gambir spans 1.32-1.34. anand/ms/srid/dhan/puru fresh
  Sanskrit-source; tej/siva/purohit/adi/chinmay/rams/prabhu fresh English/Hindi-source. Caught the
  recurring trailing-comma-adjacent bug pattern again: initial fill script left prabhu.hi/be/ka
  empty (forgot to include in FILL dict even though prabhu.en was set standalone) — empty-check
  caught it immediately, filled in a follow-up pass.
- [x] Ch1 v33 — complete (2026-07-10): 0 empty/bogus/nonstr. "Those for whose sake we desire
  kingdom, enjoyments, pleasures stand here in battle, having abandoned life and wealth."
  madhav/raman/abhinav/sankar/jaya/vallabh/venkat/neel all tag-swap reusable from v32 (byte-
  identical sa). chinmay drops to "No commentary" boilerplate. prabhu.en/hi/be/ka continue the
  same purport paragraph from v32 with only the opening line differing — reused the shared
  paragraph, translated only the new opening line. anand/ms/srid/dhan/puru + 6 English-src +
  rams fresh. san.en here is the actual "teachers, fathers, sons..." list content (confirms the
  v32 san-mismatch theory: san's content was simply shifted one verse early throughout this
  stretch).
- [x] Ch1 v34 — complete (2026-07-10): 0 empty/bogus/nonstr. "Teachers, fathers, sons, grandfathers,
  uncles, fathers-in-law, grandsons, brothers-in-law, other relatives" — the kinship-list verse.
  madhav/raman/abhinav/sankar/jaya/vallabh/venkat tag-swap from v33. rams is one long block
  spanning 1.34-1.35 (word-by-word gloss of each kinship term) — translated in full, will need to
  check at v35 whether it's simply reused verbatim (same "1.34-1.35" span) or partially fresh.
  prabhu.en/hi/be/ka: new opening line ("O Madhusudana, when teachers...") + reused the same long
  Govinda-purport paragraph verbatim from v32/v33 (3rd consecutive verse reusing this paragraph).
  san.en confirmed shifted one verse further (now showing v35's "I do not wish to slay these
  men... even for the three worlds" content) — consistent shift pattern holds. anand/ms/srid/dhan/
  puru/neel fresh Sanskrit-source.
- [x] Ch1 v35 — complete (2026-07-10): 0 empty/bogus/nonstr. "I do not wish to kill these, though
  they kill me, O Madhusudana, even for the sovereignty of the three worlds, let alone the earth."
  madhav/raman/sankar/jaya/vallabh/venkat/rams all tag-swap from v34 (rams's 1.34-1.35 span block
  reused verbatim — confirmed near-identical, only OCR whitespace noise differs). abhinav flips
  to a NEW range boilerplate "1.35-1.44" (was "1.30-1.34" range before) — required fresh
  translation, and the fill script initially forgot to include abhinav in FILL (same omission
  pattern as v32's prabhu) — caught immediately by empty-check, fixed in follow-up pass. Also
  caught a live trailing-comma bug in the neel.ka assignment *before* running the script this
  time (proactively reviewed the file for stray commas after string literals) — worth doing this
  visual check before executing every fill script from now on, not just after. san.en content
  continues its shift (now showing v36-adjacent "Dhritarashtra's sons... Janardana" material).
  prabhu.en/hi/be/ka: 4th consecutive verse reusing the same Govinda purport paragraph, new
  opening line only. anand/ms/srid/dhan/puru/neel fresh Sanskrit-source (ms notably long, covering
  aggressor/atatayi doctrine and Yajnavalkya citation).
- [x] Ch1 v36 — complete (2026-07-10): 0 empty/bogus/nonstr. "What joy from killing Dhritarashtra's
  sons, O Janardana? Only sin from killing these aggressors." madhav/raman/abhinav/sankar/jaya/
  vallabh/venkat tag-swap from v35. prabhu drops the reused Govinda-purport paragraph after 4
  verses and goes fully fresh (new content on the six types of aggressors, Rama/Ravana example,
  addressing Krishna as "Madhava"). chinmay/rams fresh with substantial content on the atatayi
  (aggressor) doctrine and dharma-shastra-vs-artha-shastra reasoning. anand/ms/srid/dhan/puru/neel
  all fresh Sanskrit-source, several quite long (dhan/puru especially, citing Yajnavalkya on smriti
  conflict resolution). san.en content matches this verse's actual meaning for the first time in
  several verses (the shift pattern may have stabilized or reset — worth re-checking at v37).
- [x] Ch1 v37 — complete (2026-07-10): 0 empty/bogus/nonstr. "Therefore we are not worthy to kill
  our own kinsmen; how could we be happy after killing them, O Madhava?" madhav/raman/abhinav/
  sankar/jaya/vallabh/venkat/neel all tag-swap from v36 (neel byte-identical again — the atatayi
  boilerplate now spans v36-v37). chinmay/rams/prabhu/6-English-src fresh. prabhu.en is
  noticeably short (805 chars vs the ~2500-char purports of v32-v36) — first mention of the
  kshatriya-obligation-to-accept-challenge theme. anand/ms/srid/dhan/puru fresh Sanskrit-source,
  covering why Duryodhana's side doesn't perceive the fault (greed-corrupted intellect) vs. why
  Arjuna's side should. san.en content matched this verse correctly again (2nd verse in a row —
  the earlier one-verse-early shift may have genuinely stabilized).
- [x] Ch1 v38 — complete (2026-07-10): 0 empty/bogus/nonstr. "Even though these do not see the
  fault, how should we, who perceive it, not know to turn away?" madhav/raman/abhinav/sankar/
  jaya/vallabh/venkat tag-swap from v37. chinmay drops to "No commentary" boilerplate; srid also
  "No commentary" this verse (both simple). rams is a long fresh block spanning 1.38-1.39,
  including the Drupada/Drona backstory of enmity between friends. prabhu.en/hi/be/ka: new 2-
  sentence opening (about destruction of family tradition/dynasty) + reused the same long Govinda
  purport paragraph verbatim yet again (5th time reusing this exact paragraph, now spanning
  v32-38). anand/ms/dhan/puru/neel fresh Sanskrit-source, with ms/neel both citing the falcon-
  sacrifice (shyena-yajna) analogy for scripturally-enjoined-but-still-sinful acts.
- [x] Ch1 v39 — complete (2026-07-10): 0 empty/bogus/nonstr. "How should we, who clearly perceive
  the fault caused by destroying the family, not know to turn away from this sin, O Janardana?"
  madhav/raman/abhinav/sankar/jaya/vallabh/venkat/srid/rams all tag-swap from v38 (srid's "No
  commentary" boilerplate and rams's 1.38-1.39 span block both reused verbatim). gambir also
  spans 1.38-1.39 and should have been tag-swapped too — the fill script's reuse loop initially
  omitted it, leaving gambir.hi/be/ka empty (en was already correct from the shared span);
  caught by the empty-check, fixed with a direct follow-up copy from v38. chinmay/prabhu fresh;
  prabhu.en/hi/be/ka: the sentence "With the destruction of the dynasty..." — which was the 2nd
  sentence of v38's fresh opening — is reused verbatim as this verse's opening, followed by a
  wholly new paragraph on varnashrama and family purification duties (breaks the 5-verse-long
  Govinda-purport-paragraph reuse streak from v32-38). anand/ms/dhan/puru/neel fresh Sanskrit-
  source, expanding on why the family's kuladharma (righteous rites) perish with its destruction.
  Lesson: when a *previous* verse's block was itself a reused multi-verse-spanning block (like
  gambir's or rams's 1.38-1.39 span), remember to check ALL blocks with that same span for
  continued reuse, not just the ones already flagged fresh by the sa-diff — the sa-diff check
  compares only consecutive verse pairs and can miss that a block reused two verses back is due
  for another verse of reuse.
- [x] Ch1 v40 — complete (2026-07-10): 0 empty/bogus/nonstr. "With destruction of the family,
  eternal kuladharmas perish; dharma destroyed, unrighteousness overtakes the whole family."
  madhav/raman/abhinav/sankar/jaya/vallabh tag-swap from v39. srid AND venkat both turned out to
  carry the identical short "adharmo'bhibhavati iti manasa-doshoktih" one-liner — venkat had been
  "no commentary" boilerplate for verses, now picked up srid's exact short gloss (an unusual
  cross-commentator coincidence, not a tag-swap since venkat's own v39 content differed — verified
  both independently rather than assuming reuse). prabhu.en/hi/be/ka continues the established
  verse-mismatch pattern (content describing women/family purity, actually v41's material) —
  translated as-is per policy. chinmay/rams fresh; rams's explanation covers why unrighteousness
  overtakes survivors (children/women) once experienced elders are killed in war. anand/ms/dhan/
  puru fresh Sanskrit-source; neel is another short stale-looking fragment (women resorting to
  other men for offspring — actually v41-adjacent content), translated as-is.
- [x] Ch1 v41 — complete (2026-07-10): 0 empty/bogus/nonstr. "From prevalence of unrighteousness,
  O Krishna, women of the family become corrupted; women corrupted, O Varshneya, varnasankara
  results." madhav/raman/abhinav/sankar/jaya/vallabh tag-swap from v40. srid AND venkat again
  share an identical short one-liner ("pradushyanti iti kayika-doshoktih") — same cross-
  commentator coincidence pattern as v40, verified independently rather than assumed. prabhu.en
  continues the established verse-mismatch shift (content about ancestors falling due to lapsed
  shraddha rites — this is actually v42's material) — translated as-is per policy. chinmay is a
  long fresh block with a notable modern-apologetic reading of varna as merit-based social role
  rather than birth caste. rams fresh, explains dharma/adharma's effect on antahkarana→buddhi
  chain leading to women's corruption. anand/ms/dhan/puru/neel fresh Sanskrit-source; neel notably
  addresses the Parashurama-widows counterexample to the pinda-lineage doctrine.
- [x] Ch1 v42 — complete (2026-07-10): 0 empty/bogus/nonstr. "Admixture of castes leads
  family-destroyers and the family to hell; their ancestors fall, deprived of rice-ball and water
  offerings." madhav/raman/abhinav/sankar/jaya/vallabh/srid/venkat all tag-swap from v41 (srid/
  venkat's short one-liner from v41 reused verbatim here too — 3rd verse now, may be a
  multi-verse-spanning block rather than coincidence as first suspected at v40/v41). prabhu.en
  finally catches up to matching v42's actual content (ancestors/pinda-udaka theme) — the
  one-verse-early shift that had been running since ~v32 appears to have resolved itself.
  chinmay/rams fresh, both explore the pinda/tarpana ancestor-worship doctrine and its social
  rationale. anand/ms/dhan/puru fresh Sanskrit-source; neel is a short one-liner pointing forward
  ("elaborates across two verses") rather than substantive content itself.
- [x] Ch1 v43 — complete (2026-07-10): 0 empty/bogus/nonstr. "By these faults of family-destroyers,
  causing admixture of castes, eternal caste-dharmas and family-dharmas are destroyed."
  madhav/raman/abhinav/sankar/jaya/vallabh/neel tag-swap from v42. srid AND venkat both drop to
  "No commentary" boilerplate this verse (matching each other again — the two commentators keep
  mirroring each other's brevity through this stretch, now 4 verses running: v40 short line,
  v41-42 the other short line, v43 both empty). prabhu.en shifts one verse further ahead (now
  showing v44's actual "I have heard by disciplic succession..." content) — the verse-mismatch
  pattern that seemed resolved at v42 has resumed; translated as-is per policy. chinmay/rams
  fresh — rams explains the kuladharma/jatidharma distinction (family-specific custom vs.
  caste-wide scriptural rule). anand/ms/dhan/puru fresh Sanskrit-source.
- [x] Ch1 v44 — complete (2026-07-10): 0 empty/bogus/nonstr. "We have heard, O Janardana, that men
  whose kuladharma is destroyed dwell in hell for an unfixed period." madhav/raman/abhinav/
  sankar/jaya/vallabh/srid/venkat/neel all tag-swap from v43 (srid/venkat both stayed "No
  commentary" for a 2nd verse running). prabhu.en shifted one verse further ahead again (now
  showing v45's "Alas, how strange..." lament content) — the mismatch offset seems to be
  increasing by one verse each time rather than resolving; translated as-is per policy, will keep
  tracking this pattern into Ch1's final verses. chinmay short/fresh; rams fresh, explains the
  free-will/discernment (vivek) doctrine behind why bad conduct leads to hell, and clarifies
  "manushyanam" includes ancestors, the family-destroyer himself, and future descendants.
  anand/ms/dhan/puru fresh Sanskrit-source; ms notably has Arjuna second-guessing his own earlier
  resolve to fight as itself already sinful.
- [x] Ch1 v45 — complete (2026-07-10): 0 empty/bogus/nonstr. "Alas, what a great sin we have
  resolved to commit, ready to kill our own kinsmen out of greed for kingdom's happiness!"
  madhav/raman/sankar/jaya/vallabh/srid/venkat/neel tag-swap from v44. abhinav required fresh
  translation (not tag-swap — content differs from v44, discusses "we" meaning all divided into
  camps, and discernment). prabhu.en shifted another verse ahead (now showing v46's "better if
  unarmed I be killed" content) — the offset has now grown to +2 verses ahead of its nominal
  file; translated as-is per policy, tracking whether it stabilizes by Ch1's end (only 2 verses
  left). chinmay/rams fresh — rams is the longest block yet this session (~3700 chars), covering
  the "aho"/"bata" grammatical analysis, a tangent reconciling this verse with Arjuna's later
  question in BG 3.36, and closing the whole "chain of calamities" argument sequence (v35-45).
  anand/ms/dhan/puru fresh Sanskrit-source.
- [x] Ch1 v46 — complete (2026-07-10): 0 empty/bogus/nonstr. "If Dhritarashtra's sons, weapons in
  hand, were to kill me unresisting and unarmed, that would be better for me." This is where
  several commentators' Chapter 1 exposition formally ends — anand/ms/neel all carry colophons
  ("इति ... प्रथमोऽध्यायः") marking end-of-chapter, so their v46 blocks were translated including
  those closing lines. Discovered Ch1 actually has 48 verse files (not 47 as previously assumed
  in memory — corrected). madhav/raman/sankar/jaya/vallabh/srid/venkat tag-swap from v45. abhinav
  fresh — a chapter-summary block spanning "1.26-1.47" (Sanjaya's frame + Arjuna's refusal
  narrative) followed by the verse's own content restated. prabhu.en jumped to the actual
  Sanjaya-narration content that belongs to the *next* file (v47) — "Arjuna cast aside his bow...
  Thus end the Bhaktivedanta purports to the First Chapter" — translated as-is; this confirms
  prabhu's offset is now consistently ~2 files ahead and likely reflects the source's own
  chapter-boundary quirk rather than a simple linear drift. chinmay/rams fresh, rams the longest
  block of the whole grind (~5250 chars) — closes out the entire "chain of calamities" argument
  with reflections on destiny, free will, and previews Arjuna's later question in BG 3.36.
  anand/ms/dhan/puru/neel fresh Sanskrit-source, several ending in colophons as noted above.
- [x] Ch1 v47 — complete (2026-07-10): 0 empty/bogus/nonstr. Sanjaya's narration verse ("Having
  spoken thus, Arjuna cast aside his bow and sat down in the chariot, grief-stricken") — the
  actual chapter-1-closing verse. Structurally unlike prior verses: no 'prabhu' key at all (Prabhupada's
  purport for this verse was the content found shifted into v46's prabhu field last verse — confirms
  the source corpus splits/merges Prabhupada's commentary across the v46/v47 boundary rather than
  a simple linear per-verse offset). Nearly every commentator field here was a **merged dump**
  combining multiple authors' end-of-chapter colophons concatenated together — most dramatically
  `anand`, whose sa field ran ~9850 chars and literally contained Dhanapati's colophon, Madhva's
  "did not comment" note, Raman/Neelakantha's shared narrative paragraph, Venkatanatha's full
  commentary+colophon, Chinmayananda's entire ~6300-char Hindi essay on Upanishad/Yoga/dharma
  philosophy (verbatim identical to the real `chinmay` block), a short Rams/Tej excerpt, a bare
  "No commentary", Jayatirtha's "did not comment" note, Madhusudana's own 2 paragraphs, Sankara's
  "did not comment" note, Vallabha's own paragraph, and Siva's word-gloss+closing — all pasted
  in sequence. Rather than re-translating this redundant content, built `anand`'s translation by
  concatenating the already-produced translations of each matching segment (in Sanskrit-dump
  order, separated by `---`), after translating only the two genuinely unique pieces (the
  Dhanapati-style paragraph and Madhusudana's own reflection on the chapter's purpose). Applied
  the same segment-sharing logic to `ms`/`puru` (share Madhusudana's 2 own paragraphs, `puru`
  stopping there while `ms` continues into the sankar/vallabh/siva tail), `dhan` (own paragraph +
  own colophon), and `srid`/`venkat`/`neel` (all carry Venkatanatha's own commentary+colophon,
  with `neel` additionally prefixing the raman/abhinav narrative paragraph). `raman` and `abhinav`
  share the same "Arjuna said - Sanjaya said..." narrative paragraph (~1050-1080 chars, praising
  Arjuna's character) with `abhinav` appending 2 more short Sanjaya-quote variants. This is by far
  the most structurally unusual verse of the 47 completed so far — a pure chapter-boundary data
  artifact, not a translation decision; corpus reuse/merge patterns should be expected to break
  down entirely at chapter transitions going forward into Ch2+.
- [x] Ch1 v48 — complete (2026-07-10): 0 empty/bogus/nonstr. This file's "slok" IS the chapter's
  closing sankalpa-vakya itself ("Om tat sat... arjuna-vishada-yogo nama prathamo'dhyayah") — every
  one of the 21 commentator blocks simply reads "[Author] did not comment on this sloka" in the
  source, since no commentator actually glosses the colophon line. Filled all 4 languages for all
  21 blocks with the equivalent "[Author] did not comment on this sloka" statement, using each
  commentator's full name. Trivial verse, immediately clean.
- **CHAPTER 1 COMPLETE: all 48 verses (v1-v48), verified 0 empty/0 bogus/0 nonstr throughout.**
- [x] Ch2 v1 — complete (2026-07-10): 0 empty/bogus/nonstr. "Sanjaya said: to him thus overcome with
  pity, his eyes filled with tears, despondent, Madhusudana spoke this word." First verse of
  Chapter 2 — full per-verse structure resumes normally (prabhu key present again, unlike the
  Ch1-closing colophon files). All 22 blocks freshly translated (no reuse possible, new chapter).
  chinmay/rams/prabhu substantial fresh commentary on Arjuna's psychological collapse.
  anand/ms/dhan/puru/neel/venkat/vallabh/raman fresh Sanskrit-source, several quite long (venkat
  ~1600 chars covering grammatical analysis of "asthane", "kripa" vs "daya", etc).
- [x] Ch2 v2 — complete (2026-07-10): 0 empty/bogus/nonstr. Krishna's first response: "From where
  has this impurity come upon you at this critical moment, Arjuna? Unbefitting the noble, not
  conducive to heaven, disgraceful." venkat tag-swap reused verbatim from v1 (block spans 1.47
  through 2.2 as one continuous grammatical commentary). All other 21 blocks fresh — ms/dhan
  notably explain the etymology of "Bhagavan" (six-fold "bhaga" enumeration) in near-identical
  passages; puru/neel/dhan debate the "aryajushtam" vs "na aryaih jushtam" word-division question.
  rams/chinmay explore why Krishna's astonishment ("kutah") functions pedagogically rather than
  from genuine not-knowing.
- [x] Ch2 v3 — complete (2026-07-10): 0 empty/bogus/nonstr. "Do not yield to impotence, Partha; it
  is unbecoming of you. Cast off this petty weakness of heart and rise, Parantapa." raman/venkat
  tag-swap reused verbatim from v2 (block spans 1.47 through 2.3 as one continuous commentary).
  vallabh's block spans 2.2-2.3 together — initial fill script forgot to reuse it from v2 (same
  omission pattern as before), caught by empty-check, fixed in follow-up. madhav/jaya/sankar "did
  not comment" boilerplate; abhinav also "no commentary" here. chinmay/rams substantial fresh
  commentary on Krishna's rhetorical strategy (silence until now, then sharp rebuke) and the
  klaibya/kshudra wordplay. anand/ms/srid/dhan/puru/neel fresh Sanskrit-source.
- [x] Ch2 v4 — complete (2026-07-10): 0 empty/bogus/nonstr. Arjuna's first reply: "How shall I
  fight, O Madhusudana, against Bhishma and Drona with arrows, O Arisudana? They are worthy of
  worship." madhav/sankar/jaya tag-swap reused (boilerplate) from v3. All 18 other blocks fresh:
  tej/siva/purohit/san/adi/gambir (short), chinmay/rams/prabhu (long, fresh commentary on
  ego/dharma and Bhishma/Drona's personal devotion to Arjuna), anand/raman/vallabh/ms/srid/dhan/
  puru/neel (Sanskrit-source, fresh). abhinav's sa spans "2.4-2.6" as one continuous block — must
  check tag-swap reuse at BOTH v5 AND v6, not just the next verse.
- [x] Ch2 v5 — complete (2026-07-10): 0 empty/bogus/nonstr. "Better to live by begging alms in this
  world than to slay these noble gurus; even killing them, desiring wealth, I would only enjoy
  blood-stained pleasures." madhav/sankar/jaya/raman/abhinav/venkat tag-swap reused verbatim from
  v4 (confirms abhinav/venkat's "2.4-2.6" span continues here as predicted). All 15 other blocks
  fresh: tej/siva/purohit/san/adi/gambir (short), chinmay/rams/prabhu (long), anand/vallabh/ms/
  srid/dhan/puru/neel (Sanskrit-source). abhinav/venkat's span still covers v6 — check tag-swap
  reuse there too before assuming fresh translation needed.
- [x] Ch2 v6 — complete (2026-07-10): 0 empty/bogus/nonstr. "We do not know which is better, to
  conquer or be conquered; those very kinsmen whom, having slain, we would not wish to live, stand
  arrayed before us." madhav/sankar/jaya/abhinav tag-swap reused from v5 — abhinav's "2.4-2.6" span
  confirmed to end exactly here (both abhinav AND venkat, which unexpectedly shared the span, are
  now DIFFERENT at v6, so both required fresh translation this verse). All 17 other blocks fresh:
  tej/siva/purohit/san/adi/gambir (short), chinmay/rams/prabhu (long), anand/raman/vallabh/ms/srid/
  dhan/venkat/puru/neel (Sanskrit-source). vallabh's sa explicitly spans "2.6-2.8" as one question
  block — check tag-swap reuse at v7 AND v8.
- [x] Ch2 v7 — complete (2026-07-10): 0 empty/bogus/nonstr (after fixing one trailing-comma bug
  live, prabhu.hi — grep pre-check missed it because the assignment used `=` not `d[...]=`, exposing
  a gap in the grep pattern; caught immediately by the isinstance check). "Overpowered by pity,
  confused about dharma, I ask You: tell me for certain what is good for me; I am Your disciple,
  instruct me who has taken refuge in You." madhav/sankar/jaya/raman/venkat/vallabh tag-swap reused
  from v6 (vallabh's new "2.6-2.8" span confirmed continuing here). All other blocks fresh:
  tej/siva/purohit/san/adi/gambir (short), chinmay/rams/prabhu (long), anand/abhinav/ms/srid/dhan/
  puru/neel (Sanskrit-source; abhinav here spans "2.7-2.10", a new multi-verse block — must check
  reuse at v8, v9, AND v10). vallabh's span still needs checking at v8 too.
- [x] Ch2 v8 — complete (2026-07-10): 0 empty/bogus/nonstr (prabhu block initially left as a bad
  self-referencing placeholder in the fill script — caught before running by re-reading the actual
  v8 prabhu source, fixed directly, then removed from the script). "Even attaining an unrivalled
  kingdom on earth or lordship over the gods, I do not see what would remove this grief drying up
  my senses." madhav/sankar/jaya/raman/abhinav/vallabh/venkat tag-swap reused from v7 (abhinav's
  "2.7-2.10" and vallabh's "2.6-2.8" spans both confirmed continuing — vallabh's span ends here).
  All other blocks fresh: tej/siva/purohit/san/adi/gambir (short), chinmay/rams/prabhu (long),
  anand/ms/srid/dhan/puru/neel (Sanskrit-source). neel's sa spans "2.8-2.9" (new) — check reuse v9.
- [x] Ch2 v9 — complete (2026-07-10): 0 empty/bogus/nonstr. Sanjaya's narration verse: "Having
  spoken thus to Hrishikesha, Gudakesha Parantapa said to Govinda, 'I will not fight,' and fell
  silent." madhav/sankar/jaya/abhinav/neel tag-swap reused from v8 (abhinav's "2.7-2.10" span
  continues — check v10 too; neel's "2.8-2.9" span ends here). All other blocks fresh: tej/siva/
  purohit/san/adi/gambir (short), chinmay/rams/prabhu (long, prabhu.en already present from Phase-1
  restructure since it's English-source), anand/raman/vallabh/ms/srid/dhan/venkat/puru
  (Sanskrit-source, venkat exceptionally long ~3200 chars covering meta-commentary on why the Gita
  teaches beyond what was asked). This is the Ch1/Ch2 dialogue's final "Arjuna falls silent" verse
  before Krishna's teaching begins at v10.
- [x] Ch2 v10 — complete (2026-07-10): 0 empty/bogus/nonstr (venkat was completely missed in the
  first fill-script pass — flagged DIFFERENT in the sa-diff but never added to FILL; caught by the
  detector's empty-check, fixed in a direct follow-up). "To that despondent Arjuna, in the midst of
  both armies, Hrishikesha, smiling as it were, spoke these words" — closing verse of Ch1/Ch2's
  narrative frame, right before Krishna's actual teaching begins at v11. madhav/jaya/raman/abhinav
  tag-swap reused from v9 (abhinav's "2.7-2.10" span ends here). sankar switched from "did not
  comment" boilerplate (which had held since early Ch1) to a genuinely fresh, very long (~6500
  char) meta-commentary explaining the purpose of the whole Ch1/Ch2 narrative frame and refuting
  the jnana-karma-samuccaya (combined-path) theory — expect sankar to require fresh translation
  from here on, not tag-swap reuse. This closes the narrative frame; v11 begins Krishna's actual
  teaching ("Shri Bhagavan said"), so expect substantially different/fresh commentary blocks
  throughout from here — the low-reuse "conch/narrative" stretch is over.
- [ ] Ch2 v11–73 — pending
- [x] Ch18 v1 — complete (2026-07-11): 0 empty/bogus/nonstr. First verse of Chapter 18. All 4 languages freshly translated using dedicated subagents' scratchpad scripts. Verified 0 empty, 0 bogus.
- [x] Ch18 v2 — complete (2026-07-11): 0 empty/bogus/nonstr. Krishna explains Tyaga and Sannyasa. All 4 languages freshly translated using subagents and merged/validated. Verified 0 empty, 0 bogus.
- [x] Ch18 v3 — complete (2026-07-11): 0 empty/bogus/nonstr. Diverse opinions of sages on whether actions should be abandoned. All 4 languages freshly translated using subagents and merged/validated. Verified 0 empty, 0 bogus.
- [x] Ch18 v4 — complete (2026-07-11): 0 empty/bogus/nonstr. Krishna's declaration on Tyaga being threefold. All 4 languages freshly translated using subagents and merged/validated. Verified 0 empty, 0 bogus.
- [x] Ch18 v5 — complete (2026-07-11): 0 empty/bogus/nonstr. Sacrifice, gift and penance must not be abandoned. All 4 languages freshly translated using subagents. Verified 0 empty, 0 bogus.
- [x] Ch18 v6 — complete (2026-07-11): 0 empty/bogus/nonstr. Actions should be performed without attachment or expectation of fruits. All 4 languages freshly translated using subagents. Verified 0 empty, 0 bogus.
- [x] Ch18 v7 — complete (2026-07-11): 0 empty/bogus/nonstr. Renunciation of prescribed duties out of delusion is Tamasic. All 4 languages freshly translated using subagents. Verified 0 empty, 0 bogus.
- [x] Ch18 v8 — complete (2026-07-11): 0 empty/bogus/nonstr. Renouncing duties out of fear of physical strain is Rajasic. All 4 languages freshly translated using subagents. Verified 0 empty, 0 bogus.
- [x] Ch18 v9 — complete (2026-07-11): 0 empty/bogus/nonstr. Performing prescribed duties as a duty, without attachment or fruit, is Sattvik. All 4 languages freshly translated using subagents. Verified 0 empty, 0 bogus.
- [x] Ch18 v10 — complete (2026-07-11): 0 empty/bogus/nonstr. A Sattvik renouncer has no aversion to disagreeable work and no attachment to agreeable work. All 4 languages freshly translated using subagents. Verified 0 empty, 0 bogus.
- [x] Ch18 v11 — complete (2026-07-11): 0 empty/bogus/nonstr. Embodied beings cannot abandon actions completely, but he who renounces action fruits is a renouncer. Translated via subagents and manual Kannada thread. Verified 0 empty, 0 bogus.
- [x] Ch18 v12 — complete (2026-07-11): 0 empty/bogus/nonstr. Threefold fruit of action (evil, good, mixed) only affects non-renouncers. Translated via subagents and manual Kannada thread. Verified 0 empty, 0 bogus.
- [x] Ch18 v13 — complete (2026-07-11): 0 empty/bogus/nonstr. Five causes for the accomplishment of all actions, as declared in Vedanta. Translated via subagents and manual Kannada thread. Verified 0 empty, 0 bogus.
- [x] Ch18 v14 — complete (2026-07-11): 0 empty/bogus/nonstr. Five factors of action (body, agent, senses, vital air/functions, divinity). Translated via subagents and manual Kannada thread. Verified 0 empty, 0 bogus.
- [x] Ch18 v15 — complete (2026-07-11): 0 empty/bogus/nonstr. Actions performed by body, speech, and mind, whether right or wrong, have these five causes. Translated via subagents and manual Kannada thread. Verified 0 empty, 0 bogus.
- [x] Ch18 v16 — complete (2026-07-11): 0 empty/bogus/nonstr. One who looks upon the absolute Self as the agent due to uncultivated understanding is a durmati. Translated via subagents and manual Kannada thread. Verified 0 empty, 0 bogus.
- [x] Ch18 v17 — complete (2026-07-12): 0 empty/bogus/nonstr. One who is free from egoistic notion does not kill and is not bound even by slaying these worlds. Translated via Hindi subagent and manual Bengali/Kannada threads (due to subagent 429 limits). Verified 0 empty, 0 bogus.
- [x] Ch18 v18 — complete (2026-07-12): 0 empty/bogus/nonstr. Knowledge, knowable, knower are incentives; instrument, act, agent are constituents. Translated all languages (hi, en, be, ka) directly via manual translation threads. Verified 0 empty, 0 bogus.
- [x] Ch18 v19 — complete (2026-07-12): 0 empty/bogus/nonstr. Knowledge, action, and doer are declared in Sankhya philosophy to be of three kinds only. Translated all languages (hi, en, be, ka) directly via manual translation threads. Verified 0 empty, 0 bogus.
- [x] Ch18 v20 — complete (2026-07-12): 0 empty/bogus/nonstr. Knowledge by which one sees the one indestructible Reality in all beings is Sattvic. Translated all languages (hi, en, be, ka) directly via manual translation threads. Verified 0 empty, 0 bogus.
- [x] Ch18 v21 — complete (2026-07-12): 0 empty/bogus/nonstr. Knowledge by which one sees various entities of distinct kinds in all beings is Rajasic. Translated all languages (hi, en, be, ka) directly via manual translation threads. Verified 0 empty, 0 bogus.
- [x] Ch18 v22 — complete (2026-07-12): 0 empty/bogus/nonstr. Knowledge which clings to a single effect as if it were the whole, without reason, is Tamasic. Translated all languages (hi, en, be, ka) directly via manual translation threads. Verified 0 empty, 0 bogus.
- [x] Ch18 v23 — complete (2026-07-12): 0 empty/bogus/nonstr. Obligatory action done without attachment, love or hatred, by a desireless agent is Sattvic. Translated all languages (hi, en, be, ka) directly via manual translation threads. Verified 0 empty, 0 bogus.
- [x] Ch18 v24 — complete (2026-07-12): 0 empty/bogus/nonstr. Action performed with egoism and great effort by one longing for gratification of desires is Rajasic. Translated all languages (hi, en, be, ka) directly via manual translation threads. Verified 0 empty, 0 bogus.
- [x] Ch18 v25 — complete (2026-07-12): 0 empty/bogus/nonstr. Action undertaken from delusion, without regard to consequences, loss, injury, or capacity is Tamasic. Translated all languages (hi, en, be, ka) directly via manual translation threads. Verified 0 empty, 0 bogus.
- [x] Ch18 v26 — complete (2026-07-12): 0 empty/bogus/nonstr. Doer who is free from attachment, egoism, endowed with patience/fortitude and enthusiasm, and neutral to success/failure is Sattvic. Translated all languages (hi, en, be, ka) directly via manual translation threads. Verified 0 empty, 0 bogus.
- [x] Ch18 v27 — complete (2026-07-12): 0 empty/bogus/nonstr. Doer who is passionate, desirous of fruits of action, greedy, harmful, impure, and subject to joy and sorrow is Rajasic. Translated all languages (hi, en, be, ka) directly via manual translation threads. Verified 0 empty, 0 bogus.
- [x] Ch18 v28 — complete (2026-07-12): 0 empty/bogus/nonstr. Doer who is unsteady, uncultured, stubborn, deceitful, malicious, lazy, despondent, and procrastinating is Tamasic. Translated all languages (hi, en, be, ka) directly via manual translation threads. Verified 0 empty, 0 bogus.
- [x] Ch18 v29 — complete (2026-07-12): 0 empty/bogus/nonstr. Krishna promises to Arjuna to fully explain the threefold divisions of intellect (Buddhi) and fortitude (Dhrti) according to Gunas. Translated all languages (hi, en, be, ka) directly via manual translation threads. Verified 0 empty, 0 bogus.
- [x] Ch18 v30 — complete (2026-07-12): 0 empty/bogus/nonstr. Intellect which correctly knows pravritti (action) and nivritti (renunciation), karya and akarya (duty and non-duty), fear and fearlessness, and bondage and liberation is Sattvic. Translated all languages (hi, en, be, ka) directly via manual translation threads. Verified 0 empty, 0 bogus.
- [x] Ch18 v31 — complete (2026-07-12): 0 empty/bogus/nonstr. Intellect which incorrectly/doubtfully understands Dharma (righteousness) and Adharma, and duty and non-duty is Rajasic. Translated all languages (hi, en, be, ka) directly via manual translation threads. Verified 0 empty, 0 bogus.
- [x] Ch18 v32 — complete (2026-07-12): 0 empty/bogus/nonstr. Intellect which, enveloped in darkness, sees Adharma as Dharma and reverses all values (understands perversely) is Tamasic. Translated all languages (hi, en, be, ka) directly via manual translation threads. Verified 0 empty, 0 bogus.
- [x] Ch18 v33 — complete (2026-07-12): 0 empty/bogus/nonstr. Unwavering fortitude (Dhrti) by which one restrains/controls the functions of mind, vital force (Prana), and senses through Yoga is Sattvic. Translated all languages (hi, en, be, ka) directly via manual translation threads. Verified 0 empty, 0 bogus.
- [x] Ch18 v34 — complete (2026-07-12): 0 empty/bogus/nonstr. Fortitude (Dhrti) by which one, out of intense attachment and desiring fruits of action, holds fast to Dharma (duty), pleasure (Kama), and wealth (Artha) is Rajasic. Translated all languages (hi, en, be, ka) directly via manual translation threads. Verified 0 empty, 0 bogus.
- [x] Ch18 v35 — complete (2026-07-12): 0 empty/bogus/nonstr. Fortitude (Dhrti) by which a foolish/stupid person does not give up sleep (indolence), fear, grief, despondency, and arrogance is Tamasic. Translated all languages (hi, en, be, ka) directly via manual translation threads. Verified 0 empty, 0 bogus.
- [x] Ch18 v36 — complete (2026-07-12): 0 empty/bogus/nonstr. Krishna introduces the threefold division of happiness, in which one rejoices by practice and attains the end of all pain. Translated all languages (hi, en, be, ka) directly via manual translation threads. Verified 0 empty, 0 bogus.
- [x] Ch18 v37 — complete (2026-07-12): 0 empty/bogus/nonstr. Happiness which is like poison at first but like nectar in the end, born of the clarity (prasada) of the intellect focused on the Self is Sattvic. Translated all languages (hi, en, be, ka) directly via manual translation threads. Verified 0 empty, 0 bogus.
- [x] Ch18 v38 — complete (2026-07-12): 0 empty/bogus/nonstr. Happiness arising from sensory contact which is like nectar at first but like poison in the end is Rajasic. Translated all languages (hi, en, be, ka) directly via manual translation threads. Verified 0 empty, 0 bogus.
- [x] Ch18 v39 — complete (2026-07-12): 0 empty/bogus/nonstr. Happiness which both in the beginning and in the sequel is delusive to the self, arising from sleep, indolence (sloth), and heedlessness is Tamasic. Translated all languages (hi, en, be, ka) directly via manual translation threads. Verified 0 empty, 0 bogus.
- [x] Ch18 v40 — complete (2026-07-12): 0 empty/bogus/nonstr. No being or entity either on earth or in heaven among the gods is free from the three Gunas born of Nature. Translated all languages (hi, en, be, ka) directly via manual translation threads. Verified 0 empty, 0 bogus.
- [ ] Ch18 v41–79 — pending
- [ ] Ch3–Ch17 — pending

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
