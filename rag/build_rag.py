#!/usr/bin/env python3
"""Embed rag/slok/<lang>/*.txt with OpenAI and upsert into Neon Postgres.

    python3 rag/build_rag.py --dry-run                 # parse + cost, no API, no DB
    python3 rag/build_rag.py --lang en                 # load English
    python3 rag/build_rag.py --lang hi --lang be       # more languages
    python3 rag/build_rag.py --lang en --limit 5        # smoke test on 5 files

Every embedding is written to a local SQLite cache (rag/.embedding_cache.sqlite)
and committed there BEFORE the Neon upsert is attempted. The OpenAI call is the
only part of this pipeline that costs money and cannot be undone, so it is never
repeated for text already embedded -- if the Neon write fails, the network drops,
or the process is killed, a re-run replays from the cache and spends nothing.

Cache key is (sha256(content), model, dimensions), so editing a source file or
changing --dimensions correctly misses the cache, while a retry always hits it.

Needs OPENAI_API_KEY and NEON_POSTGRESQL_CONNECTION_STRING in .env.
Apply rag/schema.sql once before the first load.
"""
import argparse
import array
import glob
import hashlib
import os
import sqlite3
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chunker import chunk_file, MODEL_TOKEN_LIMIT  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAG_DIR = os.path.join(ROOT, "rag", "slok")
CACHE_PATH = os.path.join(ROOT, "rag", ".embedding_cache.sqlite")
LANGS = ("en", "hi", "be", "ka", "sa")

MODEL = "text-embedding-3-small"
COST_PER_1M_TOKENS = 0.02

# OpenAI allows 2048 inputs / ~300k tokens per embeddings request; stay well under.
MAX_BATCH_ITEMS = 128
MAX_BATCH_TOKENS = 200_000
MAX_RETRIES = 6


def count_tokens_factory():
    import tiktoken
    enc = tiktoken.get_encoding("cl100k_base")
    return lambda s: len(enc.encode(s))


# ---- local embedding cache -------------------------------------------------
# Durable store of everything OpenAI has returned, so a failed Neon write, a
# dropped connection or a kill -9 never costs a second API call for the same text.

def cache_key(content, dimensions):
    h = hashlib.sha256(content.encode("utf-8")).hexdigest()
    return f"{h}:{MODEL}:{dimensions}"


def open_cache():
    conn = sqlite3.connect(CACHE_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS embedding_cache (
            key       TEXT PRIMARY KEY,   -- sha256(content):model:dimensions
            vector    BLOB NOT NULL,      -- packed float32
            n_dims    INTEGER NOT NULL
        )
    """)
    # Durability over speed: an embedding we paid for must survive a crash.
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = FULL")
    conn.commit()
    return conn


def cache_get_many(cache, keys):
    """{key: [float]} for whichever keys are already cached."""
    found = {}
    keys = list(keys)
    for i in range(0, len(keys), 500):  # stay under SQLite's variable limit
        window = keys[i:i + 500]
        placeholders = ",".join("?" * len(window))
        rows = cache.execute(
            f"SELECT key, vector FROM embedding_cache WHERE key IN ({placeholders})",
            window).fetchall()
        for key, blob in rows:
            vec = array.array("f")
            vec.frombytes(blob)
            found[key] = list(vec)
    return found


def cache_put_many(cache, items):
    """Commit (key, vector) pairs. Called before any Neon write is attempted."""
    cache.executemany(
        "INSERT OR REPLACE INTO embedding_cache (key, vector, n_dims) VALUES (?, ?, ?)",
        [(key, array.array("f", vec).tobytes(), len(vec)) for key, vec in items])
    cache.commit()


def collect_chunks(langs, count_tokens, limit=None):
    """[(lang, chunk_dict, token_count)] for every source file in the languages."""
    rows = []
    for lang in langs:
        paths = sorted(glob.glob(os.path.join(RAG_DIR, lang, "*.txt")))
        if limit:
            paths = paths[:limit]
        if not paths:
            raise SystemExit(f"no source files under {os.path.join(RAG_DIR, lang)}")
        for path in paths:
            for chunk in chunk_file(path, count_tokens):
                tokens = count_tokens(chunk["content"])
                if tokens > MODEL_TOKEN_LIMIT:
                    raise SystemExit(
                        f"{path} chunk {chunk['chunk_index']} is {tokens} tokens, "
                        f"over the {MODEL_TOKEN_LIMIT} limit -- chunker needs fixing"
                    )
                rows.append((lang, chunk, tokens))
    return rows


def batched(rows):
    """Yield batches bounded by both item count and total tokens."""
    batch, tokens = [], 0
    for row in rows:
        if batch and (len(batch) >= MAX_BATCH_ITEMS or tokens + row[2] > MAX_BATCH_TOKENS):
            yield batch
            batch, tokens = [], 0
        batch.append(row)
        tokens += row[2]
    if batch:
        yield batch


def embed(client, texts, dimensions):
    """One embeddings call, retrying on rate limits and transient server errors."""
    for attempt in range(MAX_RETRIES):
        try:
            response = client.embeddings.create(
                model=MODEL, input=texts, dimensions=dimensions)
            return [d.embedding for d in response.data]
        except Exception as exc:  # noqa: BLE001 - openai raises several transient types
            transient = any(s in type(exc).__name__ for s in ("RateLimit", "APIConnection",
                                                              "InternalServer", "Timeout"))
            if not transient or attempt == MAX_RETRIES - 1:
                raise
            delay = 2 ** attempt
            print(f"    {type(exc).__name__}, retrying in {delay}s", flush=True)
            time.sleep(delay)


def existing_content(conn, langs):
    """{(slok_id, lang, chunk_index): content} already stored, to skip unchanged work."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT slok_id, lang, chunk_index, content FROM slok_embedding "
            "WHERE lang = ANY(%s)", (list(langs),))
        return {(r[0], r[1], r[2]): r[3] for r in cur.fetchall()}


def assert_dimensions(conn, dimensions):
    """Fail fast if the table's vector width does not match --dimensions."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT atttypmod FROM pg_attribute
            WHERE attrelid = 'slok_embedding'::regclass AND attname = 'embedding'
        """)
        row = cur.fetchone()
    if row and row[0] not in (-1, dimensions):
        raise SystemExit(
            f"table is vector({row[0]}) but --dimensions is {dimensions}; "
            f"edit rag/schema.sql and recreate the table to change width"
        )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", action="append", choices=LANGS,
                    help="repeatable; default is every language")
    ap.add_argument("--dimensions", type=int, default=1536)
    ap.add_argument("--dry-run", action="store_true",
                    help="parse and price only -- no API calls, no DB connection")
    ap.add_argument("--limit", type=int, help="only the first N files per language")
    args = ap.parse_args()

    langs = args.lang or list(LANGS)
    count_tokens = count_tokens_factory()

    print(f"parsing {', '.join(langs)} ...", flush=True)
    rows = collect_chunks(langs, count_tokens, args.limit)
    total_tokens = sum(r[2] for r in rows)
    print(f"  {len(rows):,} chunks, {total_tokens:,} tokens, "
          f"max chunk {max(r[2] for r in rows):,} tokens")
    print(f"  embedding cost if all are new: ${total_tokens / 1e6 * COST_PER_1M_TOKENS:.3f}")

    if args.dry_run:
        by_section = {}
        for _, chunk, _ in rows:
            by_section[chunk["section"]] = by_section.get(chunk["section"], 0) + 1
        print("  sections:", ", ".join(f"{k}={v}" for k, v in sorted(by_section.items())))
        print("dry run -- nothing sent, nothing written")
        return 0

    from dotenv import load_dotenv
    load_dotenv(os.path.join(ROOT, ".env"))
    dsn = os.environ.get("NEON_POSTGRESQL_CONNECTION_STRING")
    if not dsn:
        raise SystemExit("NEON_POSTGRESQL_CONNECTION_STRING missing from .env")
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY missing from .env")

    import psycopg
    from openai import OpenAI

    client = OpenAI()
    cache = open_cache()
    with psycopg.connect(dsn) as conn:
        assert_dimensions(conn, args.dimensions)
        stored = existing_content(conn, langs)
        pending = [r for r in rows
                   if stored.get((r[1]["slok_id"], r[0], r[1]["chunk_index"])) != r[1]["content"]]
        skipped = len(rows) - len(pending)

        # Anything already in the local cache needs no API call, only a Neon write.
        keys = {id(r): cache_key(r[1]["content"], args.dimensions) for r in pending}
        cached = cache_get_many(cache, set(keys.values()))
        fresh = [r for r in pending if keys[id(r)] not in cached]
        fresh_tokens = sum(r[2] for r in fresh)

        print(f"  {skipped:,} already current in Neon, {len(pending):,} to write")
        print(f"  {len(pending) - len(fresh):,} served from local cache (no API cost), "
              f"{len(fresh):,} need embedding "
              f"({fresh_tokens:,} tokens, ${fresh_tokens / 1e6 * COST_PER_1M_TOKENS:.3f})")

        if not pending:
            print("nothing to do")
            return 0

        done = 0
        for batch in batched(pending):
            need = [r for r in batch if keys[id(r)] not in cached]
            if need:
                # Dedupe by content within the batch too -- e.g. repeated "did not
                # comment on this sloka" placeholders -- so identical text is only
                # ever sent to the API once, not once per occurrence.
                unique_keys = list(dict.fromkeys(keys[id(r)] for r in need))
                key_to_text = {keys[id(r)]: r[1]["content"] for r in need}
                vectors = embed(client, [key_to_text[k] for k in unique_keys], args.dimensions)
                # Persist what we just paid for BEFORE touching Neon. If the upsert
                # below fails, a re-run finds these here and spends nothing.
                cache_put_many(cache, list(zip(unique_keys, vectors)))
                cached.update(dict(zip(unique_keys, vectors)))

            with conn.cursor() as cur:
                cur.executemany(
                    """
                    INSERT INTO slok_embedding
                        (slok_id, lang, chunk_index, section, author, content, embedding)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (slok_id, lang, chunk_index) DO UPDATE SET
                        section = EXCLUDED.section,
                        author = EXCLUDED.author,
                        content = EXCLUDED.content,
                        embedding = EXCLUDED.embedding
                    """,
                    [(c["slok_id"], lang, c["chunk_index"], c["section"], c["author"],
                      c["content"], str(cached[keys[id(r)]]))
                     for r in batch for (lang, c, _) in (r,)],
                )
            conn.commit()  # per batch, so a crash loses at most one batch of DB writes
            done += len(batch)
            print(f"  {done:,}/{len(pending):,} written", flush=True)

    cache.close()
    print(f"done: {done:,} chunks upserted, {skipped:,} skipped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
