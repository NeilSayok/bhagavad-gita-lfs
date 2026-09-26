-- Vector store for the RAG pipeline (Neon Postgres + pgvector).
-- Source: rag/slok/<lang>/plain_chapter_<C>_slok_<N>.txt, chunked on section headers.
-- Embeddings: OpenAI text-embedding-3-small.
--
-- One row per (slok, language, chunk). Chunking is forced by the model's
-- 8191-token input cap: 43% of the source files exceed it whole.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS slok_embedding (
    slok_id     TEXT NOT NULL,           -- 'BG2.47', parsed from the filename
    lang        TEXT NOT NULL,           -- en | hi | be | ka | sa
    chunk_index INT  NOT NULL,           -- 0-based, order within the file
    section     TEXT NOT NULL,           -- slok | word_meanings | life_application | commentary
    author      TEXT,                    -- commentator, NULL for non-commentary sections
    content     TEXT NOT NULL,           -- exact text embedded
    embedding   vector(1536) NOT NULL,
    PRIMARY KEY (slok_id, lang, chunk_index)
);

CREATE INDEX IF NOT EXISTS idx_slok_embedding_lang ON slok_embedding (lang);

-- Run this AFTER the bulk load -- building HNSW first slows inserts substantially:
-- CREATE INDEX idx_slok_embedding_hnsw ON slok_embedding USING hnsw (embedding vector_cosine_ops);
