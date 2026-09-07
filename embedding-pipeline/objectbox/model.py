"""Verse-centric ObjectBox entities for the Bhagavad Gita corpus.

No Chapter or Theme entities by design -- this store is scoped to sloks
(verses) and everything that hangs directly off a verse: word meanings,
commentaries in every available language, and chunked embeddings for
semantic search.
"""
import objectbox
from objectbox.model.properties import (
    Id, String, Int32, Int64, Float32Vector, HnswIndex, Index, VectorDistanceType,
)

EMBEDDING_DIM = 256


@objectbox.Entity()
class Slok:
    id = Id()
    verse_id = String(index=Index())  # e.g. "BG1.1"
    chapter = Int32()
    verse = Int32()
    transliteration = String()
    speaker_hi = String()
    speaker_en = String()
    speaker_be = String()
    speaker_ka = String()
    slok_hi = String()
    slok_en = String()
    slok_be = String()
    slok_ka = String()
    life_application = String()  # en only -- no other language has this field


@objectbox.Entity()
class WordMeaning:
    id = Id()
    slok_id = Int64(index=Index())
    position = Int32()
    sanskrit = String()
    transliteration = String()
    meaning = String()  # en only in the source data


@objectbox.Entity()
class Commentary:
    id = Id()
    slok_id = Int64(index=Index())
    commentator_key = String(index=Index())
    author = String()
    text_hi = String()
    text_en = String()
    text_be = String()
    text_ka = String()
    text_sa = String()


@objectbox.Entity()
class Embedding:
    id = Id()
    slok_id = Int64(index=Index())
    chunk_id = String(index=Index())  # e.g. "BG1.1.tej.hi" or "BG1.1.tej.hi.2" for a split chunk
    kind = String()  # "verse" | "commentary"
    commentator = String()  # "" for verse chunks
    lang = String()
    text = String()  # exact chunk text that was embedded
    vector = Float32Vector(index=HnswIndex(dimensions=EMBEDDING_DIM, distance_type=VectorDistanceType.COSINE))
