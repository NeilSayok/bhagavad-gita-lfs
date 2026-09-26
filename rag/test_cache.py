#!/usr/bin/env python3
"""Self-check for the embedding cache: prove the OpenAI call is never repeated.

    python3 rag/test_cache.py

Stubs the embeddings call (so no API key and no spend), but writes to the real
Neon table using a disposable slok_id prefix, then cleans up after itself.

The property under test: once an embedding has been returned, wiping the Neon
rows and re-running must NOT call the API again -- the cache has to serve them.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_rag  # noqa: E402

calls = {"n": 0, "texts": 0}


def fake_embed(client, texts, dimensions):
    calls["n"] += 1
    calls["texts"] += len(texts)
    # Deterministic, dimension-correct, non-zero vectors.
    return [[((i + j) % 97) / 97.0 for j in range(dimensions)] for i in range(len(texts))]


def rows_in_neon(dsn, prefix):
    import psycopg
    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM slok_embedding WHERE slok_id LIKE %s", (prefix + "%",))
        return cur.fetchone()[0]


def wipe(dsn, prefix):
    import psycopg
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM slok_embedding WHERE slok_id LIKE %s", (prefix + "%",))
        conn.commit()


def main():
    from dotenv import load_dotenv
    load_dotenv(os.path.join(build_rag.ROOT, ".env"))
    dsn = os.environ.get("NEON_POSTGRESQL_CONNECTION_STRING")
    if not dsn:
        raise SystemExit("NEON_POSTGRESQL_CONNECTION_STRING missing from .env")

    os.environ.setdefault("OPENAI_API_KEY", "test-not-used")  # stubbed below
    build_rag.embed = fake_embed

    prefix = "ZZTEST"
    cache_file = os.path.join(tempfile.mkdtemp(), "cache.sqlite")
    build_rag.CACHE_PATH = cache_file

    # One synthetic file's worth of chunks, tagged so they cannot collide with real data.
    real_collect = build_rag.collect_chunks

    def collect_two(langs, count_tokens, limit=None):
        rows = real_collect(langs, count_tokens, limit=1)[:3]
        return [(lang, {**c, "slok_id": prefix + c["slok_id"]}, t) for lang, c, t in rows]

    build_rag.collect_chunks = collect_two

    argv = ["build_rag.py", "--lang", "en", "--limit", "1"]
    try:
        wipe(dsn, prefix)

        sys.argv = argv
        build_rag.main()
        first_calls, first_rows = calls["n"], rows_in_neon(dsn, prefix)
        assert first_calls > 0, "expected the stub to be called on a cold cache"
        assert first_rows == 3, f"expected 3 rows in Neon, got {first_rows}"
        assert os.path.exists(cache_file), "cache file was never created"
        print(f"  cold run: {first_calls} api call(s), {first_rows} rows in Neon")

        # Simulate "Neon write failed / data lost" while the paid-for cache survives.
        wipe(dsn, prefix)
        assert rows_in_neon(dsn, prefix) == 0

        calls["n"] = 0
        sys.argv = argv
        build_rag.main()
        assert calls["n"] == 0, f"cache miss! api was called {calls['n']} more time(s)"
        assert rows_in_neon(dsn, prefix) == 3, "rows were not restored from cache"
        print(f"  replay after losing Neon rows: {calls['n']} api calls, rows restored")

        # A third run with Neon already current should do no work at all.
        calls["n"] = 0
        sys.argv = argv
        build_rag.main()
        assert calls["n"] == 0
        print("  idempotent run: 0 api calls")

        # Changing --dimensions must miss the cache (different key), not reuse vectors.
        calls["n"] = 0
        sys.argv = argv + ["--dimensions", "256"]
        try:
            build_rag.main()
        except SystemExit as exc:
            print(f"  dimension guard fired as expected: {exc}")
        else:
            assert calls["n"] > 0, "changing dimensions must not reuse cached vectors"
            print(f"  dimension change triggered {calls['n']} fresh api call(s)")
    finally:
        wipe(dsn, prefix)

    print("PASS: embeddings are never re-purchased")
    return 0


if __name__ == "__main__":
    sys.exit(main())
