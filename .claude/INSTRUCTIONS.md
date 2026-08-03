# Subagent Batch Processing Instructions: Life Application & Theme Tagging

This document provides step-by-step operational instructions for running the **Life Application Sub-Agent** and **Theme Generator Sub-Agent** across all 719 verse files in the `slok/` directory (`bhagavadgita_chapter_<C>_slok_<N>.json`).

---

## 1. Goal & Objective

Enrich every verse JSON file in `slok/` with two new user-facing fields:
1. **`life_application`**: A single, practical, actionable instruction for modern daily life (12–22 words).
2. **`themes`**: A curated array of 1 to 3 thematic tags selected strictly from a fixed taxonomy of 15 allowed themes.

---

## 2. Target JSON Schema

In each verse file (`slok/bhagavadgita_chapter_<C>_slok_<N>.json`), insert `life_application` and `themes` at the top level, immediately after `transliteration`:

```json
{
    "_id": "BG1.1",
    "chapter": 1,
    "verse": 1,
    "speaker": {
        "hi": "धृतराष्ट्र",
        "be": "ধৃতরাষ্ট্র",
        "en": "Dhritarashtra",
        "ka": "ಧೃತರಾಷ್ಟ್ರ"
    },
    "slok": { ... },
    "transliteration": "...",
    "life_application": "Notice when fear or attachment clouds your judgment today, and step back to choose duty over personal comfort.",
    "themes": [
        "Dharma",
        "Duty",
        "Attachment"
    ],
    "tej": { ... },
    "siva": { ... }
}
```

> **Note on Immutable Fields:** Do **NOT** modify or alter `_id`, `chapter`, `verse`, `speaker`, `slok`, `transliteration`, or any existing commentator blocks (`tej`, `siva`, `chinmay`, etc.).

---

## 3. Subagent Specifications

### 3.1 Sub-Agent 1: Life Application Agent
* **Definition File:** `.claude/agents/LIFE-APPLICATION-SUBAGENT.md`
* **Input:** Verse English translation (`slok.en` or primary English commentary like `tej.commentary.en` / `siva.commentary.en`).
* **Output:** One short, concrete, actionable sentence for `life_application`.
* **Rules:**
  - Exactly **1 sentence** (12–22 words).
  - Second-person imperative or gentle instruction (*"Notice when..."*, *"Pour yourself into..."*, *"Today, do..."*).
  - Specific and practical (names a moment, feeling, or action; not an abstract virtue).
  - **Forbidden:** No Sanskrit terms, no verse citations, no "the Gita teaches" framing, no exclamation marks, no emojis, no preachy tone.

### 3.2 Sub-Agent 2: Theme Generator Agent
* **Definition File:** `.claude/agents/THEME-GENERATOR-SUBAGENT.md`
* **Input:** Verse translation and English commentary.
* **Output:** JSON array of 1 to 3 theme strings assigned to `themes`.
* **Fixed Taxonomy (15 Themes ONLY):**
  ```
  "Karma", "Dharma", "Purpose", "Mindfulness", "Leadership", "Detachment", 
  "Devotion", "Fear", "Death", "Mind", "Attachment", "Duty", "Knowledge", 
  "Self-Realization", "Equanimity"
  ```
* **Rules:**
  - Assign **only** 1 to 3 themes from the fixed list above. Never invent new tags.
  - Order themes from most central to least central for the verse.
  - Most verses need only 1–2 themes; use 3 only when clearly warranted.
  - Base selection on substantive verse & commentary meaning.

---

## 4. Execution Workflow

### Step 1: File Inventory & Status Pre-Check
Run a Python pre-check script to list all 719 files in `slok/` and identify which files already have `life_application` and `themes` populated:

```python
import glob, json

files = sorted(glob.glob("slok/*.json"))
pending = []
for f in files:
    with open(f) as fp:
        data = json.load(fp)
    if "life_application" not in data or "themes" not in data:
        pending.append(f)

print(f"Total slok files: {len(files)}, Pending: {len(pending)}")
```

### Step 2: Batch Execution Protocol
Process files chapter by chapter or in sequential batches of verses:

1. **Read Target File:** Load the complete JSON file (`slok/bhagavadgita_chapter_<C>_slok_<N>.json`).
2. **Extract Context:** Extract `slok.en` and the primary commentary (e.g. `tej.commentary.en` or `siva.commentary.en`).
3. **Invoke / Generate:**
   - Run the **Life Application** prompt to generate the single-sentence instruction.
   - Run the **Theme Generator** prompt to select 1–3 theme strings from the allowed 15-item list.
4. **Update JSON via Python:**
   Insert `life_application` and `themes` into the dictionary, then write back using `json.dump(..., ensure_ascii=False, indent=4)` with a trailing newline.
5. **Validate:** Re-open and verify immediately before proceeding to the next file.

---

## 5. Verification & Quality Assurance Checklist

After processing a batch or all 719 files, execute this automated Python validation check:

```python
import glob, json

ALLOWED_THEMES = {
    "Karma", "Dharma", "Purpose", "Mindfulness", "Leadership", "Detachment", 
    "Devotion", "Fear", "Death", "Mind", "Attachment", "Duty", "Knowledge", 
    "Self-Realization", "Equanimity"
}

files = sorted(glob.glob("slok/*.json"))
errors = []

for f in files:
    with open(f, encoding="utf-8") as fp:
        d = json.load(fp)
    
    # 1. Check life_application
    la = d.get("life_application")
    if not isinstance(la, str) or not la.strip():
        errors.append(f"{f}: 'life_application' missing or empty")
    else:
        words = la.split()
        if len(words) < 10 or len(words) > 26:
            errors.append(f"{f}: 'life_application' word count ({len(words)}) out of expected range (12-22)")
        if any(char in la for char in ["!", "🙏", "🕉️"]):
            errors.append(f"{f}: 'life_application' contains forbidden punctuation/emoji")

    # 2. Check themes
    th = d.get("themes")
    if not isinstance(th, list) or len(th) < 1 or len(th) > 3:
        errors.append(f"{f}: 'themes' must be a list of 1-3 items")
    else:
        invalid = [t for t in th if t not in ALLOWED_THEMES]
        if invalid:
            errors.append(f"{f}: 'themes' contains invalid tag(s): {invalid}")

if errors:
    print(f"Validation FAILED with {len(errors)} issues:")
    for err in errors[:20]:
        print(" -", err)
else:
    print(f"SUCCESS: All {len(files)} slok files correctly populated and verified!")
```

---

## 6. Summary of Hard Rules

1. **Never edit files manually with string replacement:** Always load with `json.load()`, mutate dict keys, and dump with `json.dump(..., ensure_ascii=False, indent=4)`.
2. **Fixed Theme List:** Never invent themes outside the 15 approved strings.
3. **Strict 1-Sentence Limit:** `life_application` must be exactly 1 sentence (12–22 words), non-preachy, and actionable today.
4. **Preserve All Internal Data:** Never touch existing verse text, translations, transliterations, or commentator blocks.
