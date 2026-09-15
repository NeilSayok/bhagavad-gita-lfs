"""Embed verse + commentary text from the slok/*.json corpus with embeddinggemma-300m.

Output: embeddings.parquet with columns id, chapter, verse, kind, commentator, text, embedding (list[float]).
"""
import glob
import json
import os

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

SLOK_DIR = os.path.join(os.path.dirname(__file__), "..", "slok")
OUT_PATH = os.path.join(os.path.dirname(__file__), "embeddings.parquet")
TRUNCATE_DIM = 256
DOC_PROMPT = "title: none | text: "

COMMENTATOR_KEYS = [
    "tej", "siva", "purohit", "chinmay", "san", "adi", "gambir", "madhav",
    "anand", "rams", "raman", "abhinav", "sankar", "jaya", "vallabh", "ms",
    "srid", "dhan", "venkat", "puru", "neel", "prabhu",
]


def load_rows():
    rows = []
    for path in sorted(glob.glob(os.path.join(SLOK_DIR, "*.json"))):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        chapter, verse = data["chapter"], data["verse"]

        verse_text = " ".join(
            t for t in (data["slok"].get("en"), data.get("life_application")) if t
        ).strip()
        if verse_text:
            rows.append({
                "id": f"{chapter}.{verse}.verse",
                "chapter": chapter,
                "verse": verse,
                "kind": "verse",
                "commentator": None,
                "text": verse_text,
            })

        for key in COMMENTATOR_KEYS:
            block = data.get(key)
            if not block:
                continue
            text = block.get("commentary", {}).get("en", "").strip()
            if text:
                rows.append({
                    "id": f"{chapter}.{verse}.{key}",
                    "chapter": chapter,
                    "verse": verse,
                    "kind": "commentary",
                    "commentator": key,
                    "text": text,
                })
    return rows


def main():
    rows = load_rows()
    print(f"loaded {len(rows)} rows "
          f"({sum(r['kind'] == 'verse' for r in rows)} verse, "
          f"{sum(r['kind'] == 'commentary' for r in rows)} commentary)")

    model = SentenceTransformer("google/embeddinggemma-300m")
    texts = [DOC_PROMPT + r["text"] for r in rows]
    embeddings = model.encode(
        texts, truncate_dim=TRUNCATE_DIM, show_progress_bar=True, batch_size=32
    )

    df = pd.DataFrame(rows)
    df["embedding"] = list(np.asarray(embeddings, dtype=np.float32))
    df.to_parquet(OUT_PATH)
    print(f"wrote {len(df)} rows to {OUT_PATH}")

    verify(df)


def verify(df):
    assert df["embedding"].iloc[0].shape[0] == TRUNCATE_DIM
    assert df["id"].is_unique
    assert not df["text"].isna().any()

    # sanity: two verses in the same chapter should be closer than two random verses
    verses = df[df["kind"] == "verse"].reset_index(drop=True)
    same_chapter = verses[verses["chapter"] == verses["chapter"].iloc[0]]
    if len(same_chapter) >= 2:
        a, b = np.stack(same_chapter["embedding"].iloc[:2])
        c, d = np.stack(verses["embedding"].iloc[[0, len(verses) // 2]])
        cos = lambda x, y: x @ y / (np.linalg.norm(x) * np.linalg.norm(y))
        same_sim, rand_sim = cos(a, b), cos(c, d)
        print(f"same-chapter sim={same_sim:.3f} vs random sim={rand_sim:.3f}")
    print("verify OK")


if __name__ == "__main__":
    main()
