You are generating word-by-word meanings for a Bhagavad Gita sloka, for a 
reading app's "Word Meaning" feature. You will be given the Sanskrit verse 
text and its English translation.

Break the verse into its individual meaningful words/word-groups (sandhi-split 
where helpful for readability), in the order they appear in the verse.

For each word, give:
- sanskrit: the word as it appears (Devanagari)
- transliteration: IAST transliteration
- meaning: a short 1-4 word English gloss (not a full sentence)

Rules:
- Cover every content word; you may omit purely grammatical particles only if 
  they carry no independent meaning.
- Keep each meaning terse — a dictionary gloss, not an explanation.
- Preserve verse word order.
- Output ONLY a JSON array of objects: 
  [{"sanskrit": "...", "transliteration": "...", "meaning": "..."}]
- No extra commentary, no markdown, no trailing text.

## Input for AI Generation
Slok.hi

