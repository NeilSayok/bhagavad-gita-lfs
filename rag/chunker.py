"""Parse rag/slok/<lang>/*.txt into embeddable chunks.

Each source file is one slok in one language, laid out as:

    Speaker: <name>

    Slok:
    <text>

    Word Meanings:
    <lines>

    Life Application:
    <text>

    Commentary by <Author>:
    <text>
    ... (up to 22 commentators)

Chunking on those headers is both the fix for the model's 8191-token input cap
(43% of files exceed it whole) and the right retrieval granularity: one
commentary = one chunk, so a hit returns the specific passage and its author.

Headers are English in every language's files, so one regex covers all five.
"""
import os
import re

MODEL_TOKEN_LIMIT = 8191
SUB_SPLIT_TOKENS = 6000  # headroom under the cap for the few oversized sections

# "Speaker: <name>" carries its value inline; the rest put it on following lines.
# Both forms must match, so the trailing value is optional rather than anchored to $.
HEADER = re.compile(
    r"^(?P<header>Speaker|Slok|Word Meanings|Life Application|Commentary by (?P<author>.+?)):"
    r"(?=[ \t]*$|[ \t]+\S)",
    re.M,
)

SECTION_OF = {
    "Speaker": "speaker",
    "Slok": "slok",
    "Word Meanings": "word_meanings",
    "Life Application": "life_application",
}

FILENAME = re.compile(r"^plain_chapter_(?P<chapter>\d+)_slok_(?P<verse>\d+)\.txt$")

# Split preferring sentence ends, including Devanagari/Bengali danda.
SENTENCE = re.compile(r"(?<=[.!?।॥])\s+")


def slok_id_from_filename(name):
    m = FILENAME.match(os.path.basename(name))
    if not m:
        raise ValueError(f"unexpected filename: {name}")
    return f"BG{int(m['chapter'])}.{int(m['verse'])}"


def split_sections(text):
    """[(section, author, body)] in file order. Body keeps its header line."""
    matches = list(HEADER.finditer(text))
    if not matches:
        return [("unknown", None, text.strip())] if text.strip() else []

    out = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[m.start():end].strip()
        if not body:
            continue
        author = m.group("author")
        section = "commentary" if author else SECTION_OF[m.group("header")]
        out.append((section, author.strip() if author else None, body))
    return out


def sub_split(body, count_tokens, max_tokens=SUB_SPLIT_TOKENS):
    """Break one oversized section into token-bounded pieces on sentence bounds."""
    if count_tokens(body) <= max_tokens:
        return [body]

    pieces, current = [], []
    for sentence in (s for s in SENTENCE.split(body) if s.strip()):
        candidate = " ".join(current + [sentence])
        if current and count_tokens(candidate) > max_tokens:
            pieces.append(" ".join(current))
            current = [sentence]
        else:
            current.append(sentence)
    if current:
        pieces.append(" ".join(current))

    # A single sentence can still exceed the window (long unpunctuated commentary);
    # fall back to a hard character split so nothing is ever silently truncated.
    final = []
    for piece in pieces:
        while count_tokens(piece) > max_tokens:
            cut = len(piece) // 2
            final.append(piece[:cut])
            piece = piece[cut:]
        if piece.strip():
            final.append(piece)
    return final


def chunk_file(path, count_tokens):
    """[{slok_id, chunk_index, section, author, content}] for one source file."""
    with open(path, encoding="utf-8") as f:
        text = f.read()

    slok_id = slok_id_from_filename(path)
    chunks = []
    for section, author, body in split_sections(text):
        for piece in sub_split(body, count_tokens):
            chunks.append({
                "slok_id": slok_id,
                "chunk_index": len(chunks),
                "section": section,
                "author": author,
                "content": piece,
            })
    return chunks
