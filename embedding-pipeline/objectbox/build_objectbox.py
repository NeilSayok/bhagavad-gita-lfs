"""Build a verse-centric ObjectBox store from slok/*.json.

Writes one Slok record per verse (everything about that verse: speaker,
slok text per script, transliteration, life_application), its WordMeanings
and Commentaries (every language present, including sa), plus a chunk-level
Embedding per verse-text and per (commentator, language) commentary block --
each chunk embedded with embeddinggemma-300m (256-dim, Matryoshka-truncated).

No chapter or theme data is included by design.
"""
import glob
import json
import os
import re

import objectbox
import torch
from sentence_transformers import SentenceTransformer

from model import Slok, WordMeaning, Commentary, Embedding

DEVICE = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")

HERE = os.path.dirname(os.path.abspath(__file__))
SLOK_DIR = os.path.join(HERE, "..", "..", "slok")
DB_DIR = os.path.join(HERE, "objectbox-db")

TRUNCATE_DIM = 256
DOC_PROMPT = "title: none | text: "
MAX_CHUNK_TOKENS = 1800  # headroom under embeddinggemma-300m's 2048-token window

COMMENTATOR_KEYS = [
    "tej", "siva", "purohit", "chinmay", "san", "adi", "gambir", "madhav",
    "anand", "rams", "raman", "abhinav", "sankar", "jaya", "vallabh", "ms",
    "srid", "dhan", "venkat", "puru", "neel", "prabhu",
]
COMMENTARY_LANGS = ["hi", "en", "be", "ka", "sa"]
COMMENTARY_TEXT_FIELD = {
    "hi": "text_hi", "en": "text_en", "be": "text_be", "ka": "text_ka", "sa": "text_sa",
}

SENTENCE_SPLIT = re.compile(r"(?<=[.!?।॥])\s+")


def chunk_text(tokenizer, text, max_tokens=MAX_CHUNK_TOKENS):
    """Split text into pieces that fit the embedding model's context window."""
    if len(tokenizer.encode(text, add_special_tokens=False)) <= max_tokens:
        return [text]

    sentences = [s for s in SENTENCE_SPLIT.split(text) if s.strip()]
    chunks, current, current_len = [], [], 0
    for sent in sentences:
        sent_len = len(tokenizer.encode(sent, add_special_tokens=False))
        if current and current_len + sent_len > max_tokens:
            chunks.append(" ".join(current))
            current, current_len = [], 0
        current.append(sent)
        current_len += sent_len
    if current:
        chunks.append(" ".join(current))

    # hard-split any piece still too long (e.g. a single run-on sentence)
    final = []
    for c in chunks:
        c_len = len(tokenizer.encode(c, add_special_tokens=False))
        if c_len <= max_tokens:
            final.append(c)
            continue
        words = c.split()
        words_per_piece = max(1, int(len(words) * max_tokens / c_len))
        for i in range(0, len(words), words_per_piece):
            final.append(" ".join(words[i:i + words_per_piece]))
    return final


def main():
    print(f"loading embeddinggemma-300m on {DEVICE}...")
    model = SentenceTransformer("google/embeddinggemma-300m", device=DEVICE)
    tokenizer = model.tokenizer

    store = objectbox.Store(directory=DB_DIR)
    slok_box = store.box(Slok)
    wm_box = store.box(WordMeaning)
    commentary_box = store.box(Commentary)
    embedding_box = store.box(Embedding)

    slok_box.remove_all()
    wm_box.remove_all()
    commentary_box.remove_all()
    embedding_box.remove_all()

    pending_chunks = []  # dicts: chunk_id, kind, commentator, lang, text, slok_id
    split_count = 0
    verse_count = 0

    paths = sorted(glob.glob(os.path.join(SLOK_DIR, "*.json")))
    for path in paths:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        chapter, verse, verse_id = data["chapter"], data["verse"], data["_id"]
        speaker, slok = data.get("speaker", {}), data.get("slok", {})

        slok_id = slok_box.put(Slok(
            verse_id=verse_id,
            chapter=chapter,
            verse=verse,
            transliteration=data.get("transliteration", "") or "",
            speaker_hi=speaker.get("hi", "") or "",
            speaker_en=speaker.get("en", "") or "",
            speaker_be=speaker.get("be", "") or "",
            speaker_ka=speaker.get("ka", "") or "",
            slok_hi=slok.get("hi", "") or "",
            slok_en=slok.get("en", "") or "",
            slok_be=slok.get("be", "") or "",
            slok_ka=slok.get("ka", "") or "",
            life_application=data.get("life_application", "") or "",
        ))
        verse_count += 1

        word_meanings = [
            WordMeaning(
                slok_id=slok_id,
                position=i,
                sanskrit=wm.get("sanskrit", "") or "",
                transliteration=wm.get("transliteration", "") or "",
                meaning=wm.get("meaning", "") or "",
            )
            for i, wm in enumerate(data.get("word_meanings", []))
        ]
        if word_meanings:
            wm_box.put(word_meanings)

        # verse-text chunk: en only, no other language has translated verse content
        verse_text = " ".join(
            t for t in (slok.get("en"), data.get("life_application")) if t
        ).strip()
        if verse_text:
            pending_chunks.append({
                "chunk_id": f"{verse_id}.verse.en", "kind": "verse",
                "commentator": "", "lang": "en", "text": verse_text, "slok_id": slok_id,
            })

        commentary_rows = []
        for key in COMMENTATOR_KEYS:
            block = data.get(key)
            if not block:
                continue
            commentary_texts = block.get("commentary", {})
            fields = {"slok_id": slok_id, "commentator_key": key, "author": block.get("author", "") or ""}
            for lang in COMMENTARY_LANGS:
                fields[COMMENTARY_TEXT_FIELD[lang]] = commentary_texts.get(lang, "") or ""
            commentary_rows.append(Commentary(**fields))

            for lang in COMMENTARY_LANGS:
                text = (commentary_texts.get(lang) or "").strip()
                if not text:
                    continue
                pieces = chunk_text(tokenizer, text)
                if len(pieces) > 1:
                    split_count += 1
                for i, piece in enumerate(pieces):
                    chunk_id = f"{verse_id}.{key}.{lang}" + (f".{i + 1}" if len(pieces) > 1 else "")
                    pending_chunks.append({
                        "chunk_id": chunk_id, "kind": "commentary",
                        "commentator": key, "lang": lang, "text": piece, "slok_id": slok_id,
                    })
        if commentary_rows:
            commentary_box.put(commentary_rows)

        if verse_count % 100 == 0:
            print(f"  ...{verse_count} verses loaded, {len(pending_chunks)} chunks queued")

    print(f"loaded {verse_count} verses, {len(pending_chunks)} chunks "
          f"({split_count} commentary blocks needed splitting)")

    print("embedding chunks...")
    texts = [DOC_PROMPT + c["text"] for c in pending_chunks]
    vectors = model.encode(texts, truncate_dim=TRUNCATE_DIM, show_progress_bar=True, batch_size=32)

    embeddings = [
        Embedding(
            slok_id=c["slok_id"], chunk_id=c["chunk_id"], kind=c["kind"],
            commentator=c["commentator"], lang=c["lang"], text=c["text"],
            vector=vec.astype("float32"),
        )
        for c, vec in zip(pending_chunks, vectors)
    ]
    PUT_BATCH = 5000  # ObjectBox caps obx_box_ids_for_put at 10,000 IDs per call
    for i in range(0, len(embeddings), PUT_BATCH):
        embedding_box.put(embeddings[i:i + PUT_BATCH])

    print(f"wrote {slok_box.count()} sloks, {wm_box.count()} word meanings, "
          f"{commentary_box.count()} commentaries, {embedding_box.count()} embeddings "
          f"to {DB_DIR}")

    verify(slok_box, embedding_box, verse_count, len(pending_chunks))
    store.close()


def verify(slok_box, embedding_box, expected_verses, expected_chunks):
    assert slok_box.count() == expected_verses, "slok count mismatch"
    assert embedding_box.count() == expected_chunks, "embedding count mismatch"
    print("verify OK")


if __name__ == "__main__":
    main()
