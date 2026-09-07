"""Semantic search test against the ObjectBox store built by build_objectbox.py.

Usage: python test_search.py "<query text>" [--top-k N]
"""
import argparse
import os

import objectbox
import torch
from sentence_transformers import SentenceTransformer

from model import Slok, Embedding

HERE = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(HERE, "objectbox-db")
DEVICE = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")

TRUNCATE_DIM = 256
QUERY_PROMPT = "task: search result | query: "


def search(store, model, query, top_k):
    embedding_box = store.box(Embedding)
    slok_box = store.box(Slok)

    query_vec = model.encode(QUERY_PROMPT + query, truncate_dim=TRUNCATE_DIM)

    # over-fetch chunks since multiple chunks (e.g. commentary in several
    # languages) can belong to the same verse -- dedupe down to top_k sloks
    hits = (
        store.box(Embedding)
        .query(Embedding.vector.nearest_neighbor(query_vec, top_k * 5))
        .build()
        .find_with_scores()
    )

    seen_sloks = set()
    results = []
    for chunk, score in hits:
        if chunk.slok_id in seen_sloks:
            continue
        seen_sloks.add(chunk.slok_id)
        slok = slok_box.get(chunk.slok_id)
        results.append((slok, chunk, score))
        if len(results) >= top_k:
            break
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    if not os.path.isdir(DB_DIR):
        raise SystemExit(f"no store found at {DB_DIR} -- run build_objectbox.py first")

    print(f"loading embeddinggemma-300m on {DEVICE}...")
    model = SentenceTransformer("google/embeddinggemma-300m", device=DEVICE)
    store = objectbox.Store(directory=DB_DIR)

    results = search(store, model, args.query, args.top_k)

    print(f"\nquery: {args.query!r}\n")
    for slok, chunk, score in results:
        snippet = chunk.text[:160].replace("\n", " ")
        print(f"BG{slok.chapter}.{slok.verse}  (score={score:.4f}, matched via {chunk.kind}:{chunk.commentator or '-'}:{chunk.lang})")
        print(f"  {slok.slok_en.strip().splitlines()[0] if slok.slok_en else ''}")
        print(f"  chunk: {snippet}...")
        print()

    store.close()


if __name__ == "__main__":
    main()
