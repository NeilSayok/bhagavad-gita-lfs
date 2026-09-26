#!/usr/bin/env python3
"""Semantic search against the slok_embedding table.

    python3 rag/query_rag.py "how do I deal with anger"
    python3 rag/query_rag.py "renunciation of action" --lang en --top-k 5
    python3 rag/query_rag.py "duty" --section commentary

Exists to prove the load is correct end to end, and as the reference query
shape for whatever consumes this later.
"""
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL = "text-embedding-3-small"

# <=> is pgvector's cosine distance; 1 - distance gives similarity.
SEARCH = """
SELECT slok_id, section, author, content,
       1 - (embedding <=> %(q)s::vector) AS score
FROM slok_embedding
WHERE lang = %(lang)s
  AND (%(section)s::text IS NULL OR section = %(section)s::text)
ORDER BY embedding <=> %(q)s::vector
LIMIT %(k)s
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--lang", default="en")
    ap.add_argument("--top-k", type=int, default=5)
    ap.add_argument("--section", help="restrict to one section, e.g. commentary")
    ap.add_argument("--dimensions", type=int, default=1536)
    args = ap.parse_args()

    from dotenv import load_dotenv
    load_dotenv(os.path.join(ROOT, ".env"))
    dsn = os.environ.get("NEON_POSTGRESQL_CONNECTION_STRING")
    if not dsn:
        raise SystemExit("NEON_POSTGRESQL_CONNECTION_STRING missing from .env")
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY missing from .env")

    import psycopg
    from openai import OpenAI

    # Same model and dimensions as the load, or the vectors are not comparable.
    vector = OpenAI().embeddings.create(
        model=MODEL, input=args.query, dimensions=args.dimensions).data[0].embedding

    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute(SEARCH, {"q": str(vector), "lang": args.lang,
                             "section": args.section, "k": args.top_k})
        hits = cur.fetchall()

    if not hits:
        print("no rows -- is the table loaded for this language?")
        return 1

    print(f"query: {args.query!r}  (lang={args.lang})\n")
    for slok_id, section, author, content, score in hits:
        label = f"{section}/{author}" if author else section
        body = " ".join(content.split())
        print(f"{score:.4f}  {slok_id:9} {label}")
        print(f"        {body[:190]}{'...' if len(body) > 190 else ''}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
