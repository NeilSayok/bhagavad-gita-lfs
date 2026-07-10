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
- [ ] Ch1 v35–48 — pending
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
