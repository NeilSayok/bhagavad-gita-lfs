# Gita JSON Issues

## Summary

Found 11 issues across 706 JSON files.

The audit inspected all 760 JSON files in the `api/` directory across structural schema, chapter/verse numbering, Sanskrit text integrity, translation alignments, word-by-word meanings, speaker attribution, commentary validity, and cross-language script purity. The dataset has 100% valid JSON syntax, zero broken internal IDs, zero invalid themes, and zero speaker mismatches. However, the audit identified several high-impact semantic, textual, and cross-script anomalies—including a systematic +1 translation shift in Chapter 13, transposed word meanings in Chapter 18 Verse 45, an English-Indic verse boundary mismatch in Chapter 1 Verses 20–21, pervasive placeholder stubs with Pratika mismatches and circular dead-ends in Abhinavagupta's commentaries across 181 files, and widespread script contamination across commentator purports.

---

## Issues

### 1. `api/slok/bhagavadgita_chapter_13_slok_1.json` through `slok_34.json`, `api/chapter-slok/13/list.json`, `api/reading/all.json`, `api/wisdom/daily.json`

- **Chapter:** 13
- **Verse:** 1 to 34 (34 consecutive verses)
- **Language:** All (Hindi, English, Bengali, Kannada)
- **Issue:** Systematic +1 translation shift in `life_application` across all 4 languages.
- **Severity:** Critical
- **Confidence:** High

**Details:**

In Chapter 13, every verse from Verse 1 through Verse 34 contains the `life_application` text corresponding to verse $N+1$:
- **Verse 13.1** (Arjuna's question: *prakṛtiṃ puruṣaṃ caiva kṣetraṃ kṣetrajñam eva ca...*) contains the life application for **Verse 13.2** (*"Understand the difference between the physical body as the field of experience and the conscious observer as knower of field"* / *"भौतिक शरीर को अनुभव का क्षेत्र और चेतन पर्यवेक्षक को क्षेत्र का ज्ञाता मानने के बीच के अंतर को समझें।"*).
- **Verse 13.2** (*idaṃ śarīraṃ kaunteya kṣetram ity abhidhīyate...*) contains the life application for **Verse 13.3** (*"Know the divine presence as the supreme knower of the field in all bodies..."* / *"समस्त शरीरों में क्षेत्र के सर्वोच्च ज्ञाता के रूप में दिव्य उपस्थिति को जानो..."*).
- **Verse 13.3** (*kṣetrajñaṃ cāpi māṃ viddhi...*) contains the life application for **Verse 13.4** (*"Hear what the field is, its nature, modifications, origin..."*).
- **Verse 13.24** (*dhyānenātmani paśyanti...*) contains the life application for **Verse 13.25** (*"Some perceive the Self by meditation, others by knowledge..."*).
- **Verse 13.25** (*anye tv evam ajānantaḥ...*) contains the life application for **Verse 13.26** (*"Others, not knowing thus, worship by hearing from others..."*).
- **Verse 13.34** (*yathā prakāśayaty ekaḥ kṛtsnaṃ lokam imaṃ raviḥ...*) contains the life application for **Verse 13.35** (*"Those who perceive with the eye of wisdom the distinction between field and knower..."*).
- **Verse 13.35** contains a duplicate/rephrased application for Verse 35 (*"Distinguish between physical body and inner witness today..."*).

**Root Cause:**
In standard 34-verse recensions (such as Shankaracharya's tradition), Chapter 13 begins directly with *idaṃ śarīraṃ kaunteya* as Verse 1, omitting Arjuna's opening question. In the 35-verse recension adopted in this repository, Arjuna's question was inserted as Verse 1 (*BG13.1*). While Sanskrit sloks, transliterations, word meanings, and commentaries were correctly mapped to the 35-verse numbering (1..35), the `life_application` dataset was imported from a 34-verse source without applying the +1 offset shift. Consequently, Verse 1 has no dedicated life application for Arjuna's inquiry, and Verses 1–34 are all misaligned by exactly one verse.

This error cascades directly into:
- `api/slok/bhagavadgita_chapter_13_slok_1.json` through `slok_34.json` (34 files)
- `api/chapter-slok/13/list.json` (34 entries)
- `api/reading/all.json` (Chapter 13 entries)
- `api/wisdom/daily.json` (Entry 0 for `BG13.25` displays the teaching of Verse 13.26).

**Agents consulted:**
- DB-MIGRATION-AGENT
- LIFE-APPLICATION-SUBAGENT
- SA-TRANSLATION-SUBAGENT
- EN-TRANSLATION-SUBAGENT
- HI-TRANSLATION-SUBAGENT

---

### 2. `api/slok/bhagavadgita_chapter_18_slok_45.json`

- **Chapter:** 18
- **Verse:** 45
- **Language:** All (Sanskrit, Hindi, English, Bengali, Kannada)
- **Issue:** The `word_meanings` array belongs to a completely different verse (Chapter 5 Verse 10).
- **Severity:** Critical
- **Confidence:** High

**Details:**

The Sanskrit text of Chapter 18 Verse 45 is:
> *स्वे स्वे कर्मण्यभिरतः संसिद्धिं लभते नरः | स्वकर्मनिरतः सिद्धिं यथा विन्दति तच्छृणु*
> (*sve sve karmaṇy abhirataḥ saṃsiddhiṃ labhate naraḥ / svakarmanirataḥ siddhiṃ yathā vindati tac chṛṇu*)

However, the `word_meanings` array in `api/slok/bhagavadgita_chapter_18_slok_45.json` defines:
- `ब्रह्मणि` (*brahmaṇi* / "in Brahman")
- `आधाय` (*ādhāya* / "having placed")
- `कर्माणि` (*karmāṇi* / "actions")
- `सङ्गम्` (*saṅgam* / "attachment")
- `त्यक्त्वा` (*tyaktvā* / "having abandoned")
- `करोति` (*karoti* / "performs")
- `यः` (*yaḥ* / "who")

These words are the exact Sanskrit vocabulary of **Chapter 5 Verse 10**:
> *ब्रह्मण्याधाय कर्माणि सङ्गं त्यक्त्वा करोति यः | लिप्यते न स पापेन पद्मपत्रमिवाम्भसा*
> (*brahmaṇy ādhāya karmāṇi saṅgaṃ tyaktvā karoti yaḥ...*)

None of the actual words of Chapter 18 Verse 45 (*sve*, *karmaṇi*, *abhirataḥ*, *saṃsiddhim*, *labhate*, *naraḥ*, *svakarmanirataḥ*, *siddhim*, *yathā*, *vindati*, *tat*, *śṛṇu*) appear in the file's `word_meanings`.

**Agents consulted:**
- WORD-MEANING-SUBAGENT
- SA-TRANSLATION-SUBAGENT
- DB-MIGRATION-AGENT

---

### 3. `api/slok/bhagavadgita_chapter_1_slok_20.json` & `slok_21.json`

- **Chapter:** 1
- **Verse:** 20 and 21
- **Language:** English (`en`) vs Indic (`hi`, `be`, `ka`)
- **Issue:** The third hemistich/line of Verse 1.20 was omitted from English and prepended to Verse 1.21.
- **Severity:** High
- **Confidence:** High

**Details:**

In `api/slok/bhagavadgita_chapter_1_slok_20.json`:
- Hindi, Bengali, and Kannada include all 3 lines spoken by Sanjaya:
  1. `अथ व्यवस्थितान्दृष्ट्वा धार्तराष्ट्रान् कपिध्वजः |`
  2. `प्रवृत्ते शस्त्रसम्पाते धनुरुद्यम्य पाण्डवः |`
  3. `हृषीकेशं तदा वाक्यमिदमाह महीपते` (*"O King, he then spoke these words to Hrishikesha"*)
- English `slok` and `transliteration` contain only the first 2 lines:
  ```text
  atha vyavasthitāndṛṣṭvā dhārtarāṣṭrān kapidhvajaḥ .
  pravṛtte śastrasampāte dhanurudyamya pāṇḍavaḥ
  ```
  The third line (*hṛṣīkeśaṃ tadā vākyam idam āha mahīpate*) is missing.

In `api/slok/bhagavadgita_chapter_1_slok_21.json`:
- Hindi, Bengali, and Kannada contain only 2 lines under speaker **Arjuna**:
  1. `अर्जुन उवाच |`
  2. `सेनयोरुभयोर्मध्ये रथं स्थापय मेऽच्युत`
- English `slok` and `transliteration` have 3 lines, prepending the missing third line from Verse 20:
  ```text
  hṛṣīkeśaṃ tadā vākyamidamāha mahīpate .
  arjuna uvāca .
  senayorubhayormadhye rathaṃ sthāpaya me.acyuta
  ```
- Furthermore, `word_meanings` for *hṛṣīkeśam*, *tadā*, *vākyam*, *idam*, *āha*, *mahīpate* are defined in file `slok_21.json` (where speaker is tagged as Arjuna), even though these words are spoken by Sanjaya addressing King Dhritarashtra (*mahīpate*).

This discrepancy is also present in `api/chapter-slok/1/list.json` and `api/reading/all.json`.

**Agents consulted:**
- SA-TRANSLATION-SUBAGENT
- EN-TRANSLATION-SUBAGENT
- WORD-MEANING-SUBAGENT

---

### 4. `api/slok/bhagavadgita_chapter_4_slok_1.json`, `api/home/verseofday.json`, and 180 other files in `api/slok/`

- **Chapter:** Multiple (Chapters 3, 4, 5, 10, 11, 12, 13, 14, 15, 16, 17, 18)
- **Verse:** Multiple (181 verses with `abhinav` commentary)
- **Language:** All (English, Hindi, Bengali, Kannada)
- **Issue:** Placeholder stub commentaries, Pratika mismatches (quoting words from other verses), broken cross-references, circular dead-ends, and unlinked "wild goose chases" in Abhinavagupta's commentary.
- **Severity:** High
- **Confidence:** High

**Details:**

Across 181 files, Abhinavagupta's commentary contains uninformative placeholder stubs instead of verse commentary, confusing cross-verse Pratika quotations, broken circular references, and UX-breaking redirection directives:

1. **The "Wild Goose Chase" & Pratika Mismatch in Verse 4.1 (`api/slok/bhagavadgita_chapter_4_slok_1.json` & `api/home/verseofday.json`):**
   - The Sanskrit verse 4.1 begins: *इमं विवस्वते योगं प्रोक्तवानहमव्ययम्* (*imaṃ vivasvate yogaṃ...*).
   - The word *एवम्* (*evam*) does NOT appear anywhere in Verse 4.1; it is the opening word of Verse 4.2 (*एवं परम्पराप्राप्तम्...*).
   - However, `abhinav.commentary` across all 4 vernacular languages states:
     - `en`: `"Sri Abhinavagupta states: "Evam etc."—see detailed commentary under Verse 4.3."`
     - `hi`: `"श्री अभिनवगुप्त कहते हैं: "एवम् इत्यादि"—आगे के श्लोक (4.3) में विस्तृत व्याख्या द्रष्टव्य है।"`
     - `be`: `"শ্রী অভিনবগুপ্ত বলেছেন: "এৱম্ ইত্যাদি"—পরের শ্লোকে (৪.৩) বিস্তারিত ব্যাখ্যা দ্রষ্টব্য।"`
     - `ka`: `"ಶ್ರೀ ಅಭಿನವಗುಪ್ತರು ಹೇಳುತ್ತಾರೆ: "ಏವಮ್ ಇತ್ಯಾದಿ"—ಮುಂದಿನ ಶ್ಲೋಕದಲ್ಲಿ (೪.೩) ವಿವರವಾದ ವ್ಯಾಖ್ಯಾನವನ್ನು ನೋಡಿ"`
   - **Why this fails the user:**
     - **Irrelevant Pratika:** A user reading Verse 4.1 sees `"Evam etc."` as the heading quotation. Since Verse 4.1 begins with *"Imaṃ vivasvate"*, quoting a non-existent word from the next verse makes the data appear corrupt and nonsensical.
     - **Forced Navigation (The Wild Goose Chase):** The user is reading Verse 4.1 to understand Krishna imparting wisdom to the Sun-god Vivasvan. Instead of explaining the verse, the app presents raw unlinked text instructing them: *"see detailed commentary under Verse 4.3"*. The user has to leave the verse, scroll through the chapter list, open Verse 4.3, and find Abhinavagupta's entry.
     - **The Deceptive Empty Promise:** When the user arrives at Verse 4.3, they find only a brief 2-sentence note: *"Through these slokas the Lord shows that this selfless Yoga is ancient and eternal; because Arjuna is His devotee and friend, this supreme secret is declared today."* It discusses only devotion and friendship between Krishna and Arjuna; it contains **zero** explanation of Verse 4.1 and **no** "detailed commentary". The user was sent on a multi-step detour for an empty reward.
   - **Home Screen Impact:** Verse 4.1 is hardcoded as the featured verse in `api/home/verseofday.json`. Any user opening the application's home screen and checking commentator views immediately encounters this broken placeholder stub.

2. **The "Phantom Commentary" Pattern Across 30 Verses (Chapters 3, 4, 5):**
   - 30 verses in Chapters 3, 4, and 5 use the exact formula: `"Sri Abhinavagupta states: "<Pratika> etc."—see detailed commentary under Verse X.Y."`
   - In all 30 cases, the referenced target verse does not actually contain a detailed verse-by-verse commentary; it only contains a brief 2-line summary of that target verse.
   - **Severe examples:** In **Verse 4.7** (*yadā yadā hi dharmasya glānir bhavati bhārata...*) and **Verse 4.8** (*paritrāṇāya sādhūnāṃ...*), the commentary states:
     `"Sri Abhinavagupta states: "Bahuni etc."—see detailed commentary under Verse 4.9."`
     Neither verse contains the word *Bahuni* (which belongs exclusively to Verse 4.5: *bahūni me vyatītāni...*). A user reading one of the most famous declarations in the entire Bhagavad Gita is told to abandon the verse and go to Verse 4.9!

3. **Print-to-Digital Scraping Artifact vs. Atomic API Architecture:**
   - In physical printed books, commentators group verses (*evam ity ādi uttamam ity antam*) and editors insert cross-references (*"see v. 4.3"*) because both verses appear on the same physical paper page, allowing readers to glance down.
   - In an atomic REST API designed for mobile and web applications (`api/slok/bhagavadgita_chapter_4_slok_1.json`), each verse is an independent, isolated screen. Dumping raw print-book cross-reference strings into single-verse JSON records violates the API contract, breaks the user reading flow, and renders the endpoint useless.

4. **Fabrication of Stubs for Absent Commentaries:**
   - In the historical *Gītārtha-saṅgraha*, Abhinavagupta **did not write a commentary on Verse 4.1**. He began commenting at Verse 4.2.
   - Rather than omitting the `"abhinav"` key or honestly noting the absence of commentary, the dataset compiler cloned the Sanskrit commentary of 4.2–4.3 into 4.1, fabricated a redirect in English, Hindi, Bengali, and Kannada pointing to 4.3, and prefixed it with the Pratika of Verse 4.2 (*"Evam"*).

5. **Broken Dead-Ends and Circular Reference Loops:**
   - **Verses 10.2, 10.3, 10.4, 10.5:** All point to 10.5 in English, but Verse 10.5 itself in English literally states: `"See Comment under 10.5"`. The user is trapped in an infinite loop with **zero English commentary anywhere** for the entire sequence.
   - **Verses 18.36, 18.37, 18.38, 18.39:** Verses 18.36–18.38 state `"See Comment under 18.39"`, while Verse 18.39 states: `"(For English commentary, see 18.36-39 under 18.39.)"`. No English commentary exists for any of the four verses.
   - **Verse 17.14:** Points to 17.15, which in turn points to 17.16 (chained placeholder).

6. **Remediation Recommendations:**
   - **Truthful Omission:** If an author did not comment on a verse (e.g. 4.1), omit the author block or state explicitly: *"Sri Abhinavagupta does not comment on this verse."*
   - **In-Situ Shared Commentary:** Where an author commented on a group of verses jointly (e.g. 4.2–4.3, 4.5–4.9, 18.36–18.39), provide the complete joint commentary text directly inside each affected verse file with explicit scope: *"Sri Abhinavagupta (commenting on verses 4.2–4.3 jointly): ..."*. Never require the user to navigate to another verse.
   - **Resolve Circular Pointers:** Replace all circular/self-referential stubs in Chapters 10 and 18 with actual translated purports.

**Agents consulted:**
- SA-TRANSLATION-SUBAGENT
- EN-TRANSLATION-SUBAGENT
- HI-TRANSLATION-SUBAGENT
- BE-TRANSLATION-SUBAGENT
- KA-TRANSLATION-SUBAGENT
- DB-MIGRATION-AGENT

---

### 5. `api/slok/*.json` (276 files with Devanagari in Bengali Commentary)

- **Chapter:** Multiple (Chapters 1 to 18)
- **Verse:** Multiple
- **Language:** Bengali (`be`)
- **Issue:** 684 occurrences of unrendered Devanagari words and fragments embedded inside Bengali commentary strings across 276 files.
- **Severity:** Medium
- **Confidence:** High

**Details:**

Numerous commentator purports in Bengali contain untransliterated or untranslated Devanagari words directly mixed into Bengali sentences. Notable examples include:
- `api/slok/bhagavadgita_chapter_8_slok_21.json` (`.rams.commentary.be`): contains `तथा` in Devanagari: `'...তাকেই পরম গতি বলে तथा'`.
- `api/slok/bhagavadgita_chapter_8_slok_22.json` (`.prabhu.commentary.be`): contains `विराजमान` in Devanagari: `'...অনন্য ভক্তি দ্বারা লাভ করা যায়... विराजमान'`.
- `api/slok/bhagavadgita_chapter_9_slok_12.json` (`.gambir.commentary.be`): contains `ज्ञान` in Devanagari: `'ব্যর্থ আশা বিশিষ্ট, ব্যর্থ কর্ম বিশিষ্ট এবং ব্যর্থ ज्ञान বিশিষ্ট'`.
- `api/slok/bhagavadgita_chapter_9_slok_18.json` (`.adi.commentary.be`): contains `साक्षी` in Devanagari: `'গতি, ভর্তা, প্রভু, साक्षी, নিবাস, শরণ, সুহৃত্...'`.
- `api/slok/bhagavadgita_chapter_9_slok_8.json` (`.dhan.commentary.be`): contains `द्वारा` in Devanagari: `'...কর্ম-পরবশতার द्वारा'`.
- `api/slok/bhagavadgita_chapter_9_slok_7.json` (`.gambir.commentary.be`): contains `प्रकृति` in Devanagari: `'...সব ভূত আমার प्रकृतिকে প্রাপ্ত হয়;'`.
- `api/slok/bhagavadgita_chapter_9_slok_16.json` (`.anand.commentary.be`): contains `कारणरूप` in Devanagari.
- `api/slok/bhagavadgita_chapter_10_slok_16.json` (`.dhan.commentary.be`): contains `प्रार्थन` in Devanagari.

These Devanagari intrusions degrade readability for Bengali readers and represent incomplete localization.

**Agents consulted:**
- BE-TRANSLATION-SUBAGENT
- SA-TRANSLATION-SUBAGENT

---

### 6. `api/slok/*.json` (169 files with Devanagari in Kannada Commentary)

- **Chapter:** Multiple (Chapters 1 to 18)
- **Verse:** Multiple
- **Language:** Kannada (`ka`)
- **Issue:** 335 occurrences of Devanagari characters and words embedded in Kannada commentary strings across 169 files.
- **Severity:** Medium
- **Confidence:** High

**Details:**

Multiple Kannada commentary fields contain untranslated Devanagari fragments, digits, and words:
- `api/slok/bhagavadgita_chapter_9_slok_21.json` (`.raman.commentary.ka`): contains Devanagari `ानु` in the middle of Ramanuja's Kannada name: `ಶ್ರೀ ರಾಮानुಜರು ಹೇಳುತ್ತಾರೆ`.
- `api/slok/bhagavadgita_chapter_10_slok_6.json` (`.raman.commentary.ka`): same error (`ಶ್ರೀ ರಾಮानुಜರು`).
- `api/slok/bhagavadgita_chapter_10_slok_25.json` (`.purohit.commentary.ka`): contains Devanagari `ॐ` instead of Kannada `ಓಂ`.
- `api/slok/bhagavadgita_chapter_11_slok_1.json` (`.ms.commentary.ka`): contains `गुह्यम्ो` in Devanagari embedded in Kannada text.
- `api/slok/bhagavadgita_chapter_11_slok_1.json` (`.venkat.commentary.ka`): contains Devanagari digit `३`.
- `api/slok/bhagavadgita_chapter_10_slok_15.json` (`.venkat.commentary.ka`): contains Devanagari prefix `अनुप`.

**Agents consulted:**
- KA-TRANSLATION-SUBAGENT
- SA-TRANSLATION-SUBAGENT

---

### 7. `api/slok/*.json` (133 files with Bengali Script in Kannada Commentary)

- **Chapter:** Multiple (Chapters 1 to 18)
- **Verse:** Multiple
- **Language:** Kannada (`ka`)
- **Issue:** 181 occurrences of Bengali script characters and words embedded in Kannada commentary strings across 133 files.
- **Severity:** Medium
- **Confidence:** High

**Details:**

Due to automated cross-language conversion artifacts, Bengali characters were inadvertently inserted into Kannada sentences:
- `api/slok/bhagavadgita_chapter_8_slok_22.json` (`.gambir.commentary.ka`): uses Bengali letter `ত` (U+09A4) inside the Kannada word `ಅಂತರ್ಗতದಲ್ಲಿ` instead of Kannada `ತ` (U+0CA4).
- `api/slok/bhagavadgita_chapter_10_slok_1.json` (`.abhinav.commentary.ka`): contains the Bengali word `পূর্বে` inside Kannada commentary.
- `api/slok/bhagavadgita_chapter_10_slok_1.json` (`.prabhu.commentary.ka`): contains the Bengali character `ঐ` inside Kannada text.
- `api/slok/bhagavadgita_chapter_10_slok_17.json` (`.srid.commentary.ka`): contains the Bengali characters `ধর`.
- `api/slok/bhagavadgita_chapter_9_slok_9.json` (`.ms.commentary.ka`): contains Bengali characters in quotation marks.
- `api/slok/bhagavadgita_chapter_9_slok_34.json` (`.anand.commentary.ka`, `.raman.commentary.ka`, `.sankar.commentary.ka`, `.vallabh.commentary.ka`): contain Bengali characters mixed into Sanskrit quote transcriptions.

**Agents consulted:**
- KA-TRANSLATION-SUBAGENT
- BE-TRANSLATION-SUBAGENT

---

### 8. `api/slok/*.json` (90 files with Bengali Characters in Hindi Commentary)

- **Chapter:** Multiple
- **Verse:** Multiple
- **Language:** Hindi (`hi`)
- **Issue:** 92 occurrences of Bengali characters embedded in Hindi commentary strings across 90 files.
- **Severity:** Low
- **Confidence:** High

**Details:**

- In 88 files (e.g. `api/slok/bhagavadgita_chapter_11_slok_12.json`, `slok_15.json`, `slok_24.json`, `slok_45.json` under `.rams.commentary.hi`), the Bengali currency/double danda `৷৷` (U+09F7) was used instead of the standard Devanagari double danda `।।` (U+0965).
- In `api/slok/bhagavadgita_chapter_11_slok_25.json` (`.prabhu.commentary.hi`), the Bengali suffix `কারী` appears inside a Hindi sentence.
- In `api/slok/bhagavadgita_chapter_8_slok_4.json` (`.prabhu.commentary.hi`), Bengali characters appear in the commentary text.

**Agents consulted:**
- HI-TRANSLATION-SUBAGENT
- BE-TRANSLATION-SUBAGENT

---

### 9. `api/slok/*.json` (21 files with Kannada Characters in Bengali Commentary)

- **Chapter:** Multiple (e.g. Chapter 11)
- **Verse:** Multiple
- **Language:** Bengali (`be`)
- **Issue:** 21 occurrences of isolated Kannada characters and vowel signs embedded in Bengali commentary strings across 21 files.
- **Severity:** Low
- **Confidence:** High

**Details:**

Isolated Kannada dependent vowel signs and consonants appear embedded inside Bengali commentary strings:
- `api/slok/bhagavadgita_chapter_11_slok_16.json` (`.jaya.commentary.be`): Kannada vowel sign `ೂ` (U+0CC2).
- `api/slok/bhagavadgita_chapter_11_slok_19.json` (`.rams.commentary.be`): Kannada vowel sign `ು` (U+0CBF).
- `api/slok/bhagavadgita_chapter_11_slok_2.json` (`.venkat.commentary.be`): Kannada characters `ಿತ`.
- `api/slok/bhagavadgita_chapter_11_slok_23.json` (`.rams.commentary.be`): Kannada vowel sign `ೂ`.
- `api/slok/bhagavadgita_chapter_11_slok_40.json` (`.sankar.commentary.be`): Kannada character `ಸಿ`.

**Agents consulted:**
- BE-TRANSLATION-SUBAGENT
- KA-TRANSLATION-SUBAGENT

---

### 10. `api/slok/bhagavadgita_chapter_13_slok_21.json` & `chapter_14_slok_9.json`

- **Chapter:** 13 and 14
- **Verse:** 13.21 and 14.9
- **Language:** Hindi (`hi`)
- **Issue:** Isolated Kannada digits and characters in Hindi commentary strings.
- **Severity:** Low
- **Confidence:** High

**Details:**

- `api/slok/bhagavadgita_chapter_13_slok_21.json` (`.venkat.commentary.hi`): contains Kannada digits `೨೨` (22) embedded in Hindi text.
- `api/slok/bhagavadgita_chapter_14_slok_9.json` (`.prabhu.commentary.hi`): contains Kannada characters `ಿಕ` inside Hindi commentary text.

**Agents consulted:**
- HI-TRANSLATION-SUBAGENT
- KA-TRANSLATION-SUBAGENT

---

### 11. `api/home/verseofday.json`, `api/wisdom/daily.json`, `api/reading/all.json`

- **Chapter:** Multiple
- **Verse:** Multiple
- **Language:** All (Hindi, English, Bengali, Kannada)
- **Issue:** Trailing verse numbering and double dandas (e.g. `||४-१||`, `||1-20||`) remain in auxiliary API files while stripped from primary slok files.
- **Severity:** Low
- **Confidence:** High

**Details:**

In the primary API directories (`api/slok/`, `api/chapter-slok/`, `api/slok-colophon/`), all trailing verse numbers and enclosing double dandas (such as `||१-२२||`, `||1-22||`, `||১-২২||`, `||೧-೨೨||`) were removed to provide clean verse texts.
However, the auxiliary API endpoints were excluded:
- `api/home/verseofday.json`: contains `||४-१||` in `verse.transliteration` and `verse_text.slok`.
- `api/wisdom/daily.json`: all 10 daily wisdom verses contain trailing double dandas and verse numbers (e.g. `||१३-२५||`, `||३-३६||`).
- `api/reading/all.json`: all 701 verses retain trailing double dandas and numbers (e.g. `||1-1||`, `||1-2||`).

This leads to schema and formatting inconsistency when client applications query different API endpoints for the same verse.

**Agents consulted:**
- DB-MIGRATION-AGENT
