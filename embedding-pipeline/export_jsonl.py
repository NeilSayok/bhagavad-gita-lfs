"""Convert embeddings.parquet into embeddings.jsonl (one row per line) for the
Kotlin/JVM ObjectBox importer to consume without needing a Parquet reader.
"""
import json
import os

import pandas as pd

IN_PATH = os.path.join(os.path.dirname(__file__), "embeddings.parquet")
OUT_PATH = os.path.join(os.path.dirname(__file__), "embeddings.jsonl")


def main():
    df = pd.read_parquet(IN_PATH)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        for row in df.itertuples(index=False):
            f.write(json.dumps({
                "id": row.id,
                "chapter": int(row.chapter),
                "verse": int(row.verse),
                "kind": row.kind,
                "commentator": row.commentator,
                "text": row.text,
                "embedding": [float(x) for x in row.embedding],
            }, ensure_ascii=False) + "\n")
    print(f"wrote {len(df)} rows to {OUT_PATH}")


if __name__ == "__main__":
    main()
