# RAG query rules — slok_embedding

Rules for querying the `slok_embedding` table on Neon. `rag/query_rag.py` is a
minimal reference implementation and does **not** follow rule 1 below by
default — read that rule before trusting its raw output for a "top N sloks" ask.

## Schema recap

```
slok_embedding(slok_id, lang, chunk_index, section, author, content, embedding)
PRIMARY KEY (slok_id, lang, chunk_index)
```

One row = one chunk, not one slok. A single slok (e.g. `BG2.40`) has one row
per section — `speaker`, `slok`, `word_meanings`, `life_application`, and one
row **per commentator** under `section='commentary'` (up to 22). So a plain
top-N-by-similarity query returns N *chunks*, which can be far fewer than N
distinct sloks if one slok's commentary dominates the results.

`sa` (Sanskrit) has no `speaker`/`slok`/`word_meanings`/`life_application` rows
— commentary only, and only where a Sanskrit-language commentary source exists.

## Rule 1 — dedupe to distinct sloks when the ask is "top N sloks"

If the request is "give me N sloks" (not "give me N passages/chunks"), do not
`LIMIT N` on the raw similarity-ordered rows — that returns N chunks, and a
single slok's multiple commentary rows can crowd out other, more relevant
sloks entirely. Rank chunks within each slok first, then take each slok's best
chunk, then limit:

```sql
SELECT slok_id, section, author, content, score FROM (
    SELECT slok_id, section, author, content,
           1 - (embedding <=> %(q)s::vector) AS score,
           row_number() OVER (PARTITION BY slok_id ORDER BY embedding <=> %(q)s::vector) AS rn
    FROM slok_embedding
    WHERE lang = %(lang)s
) ranked
WHERE rn = 1
ORDER BY score DESC
LIMIT %(k)s
```

`query_rag.py`'s query does the naive version (`ORDER BY ... LIMIT k` with no
dedupe) — fine for "show me relevant passages," wrong for "show me N sloks."

## Rule 2 — embed the query with the exact model and dimensions the table was built with

Currently: `text-embedding-3-small`, `dimensions=1536`. A query vector at a
different dimension count either errors (`different vector dimensions`) or, if
you disable that check, returns meaningless distances — pgvector does not warn
you, it just computes a number. Check `rag/build_rag.py`'s `--dimensions`
default (or `SELECT vector_dims(embedding) FROM slok_embedding LIMIT 1`) before
assuming.

## Rule 3 — cast every nullable parameter, or Postgres can't infer its type

```sql
AND (%(section)s::text IS NULL OR section = %(section)s::text)
```

Without `::text` on a parameter that might be bound as `NULL`, psycopg/Postgres
throws `AmbiguousParameter` / `could not determine data type of parameter`.
This was a real bug hit and fixed in `query_rag.py` — don't reintroduce it by
copying the pattern without the cast.

## Rule 4 — `<=>` is cosine *distance*, not similarity

`ORDER BY embedding <=> %(q)s::vector` ascending gives nearest-first (correct
for `LIMIT`). To display a score people read as "higher is better," compute
`1 - (embedding <=> ...)` — OpenAI embeddings are L2-normalized so this equals
cosine similarity, range roughly `[-1, 1]`, typically `0.3`–`0.7` for genuinely
relevant Gita passages given the corpus (not `0.9`+; don't treat sub-0.9 scores
as "no match").

## Rule 5 — filter by `lang`, always

Every query should have `WHERE lang = ...`. Omitting it searches across all 5
languages at once — the same slok's `en` and `hi` chunks are different vectors
(embedded independently), and mixing them into one ranked list produces
results with no coherent interpretation across languages. There's no default;
pick one.

## Rule 6 — `section` filter narrows scope, doesn't change ranking logic

Add `AND section = 'commentary'` (or `word_meanings` / `slok` / `life_application`
/ `speaker`) to restrict which kind of text can match, e.g. "find commentary
passages about X" vs "find verses whose Sanskrit text is about X." Combine with
Rule 1's dedupe if you still want distinct sloks within that section filter.

## Rule 7 — HNSW is approximate

An HNSW index (`idx_slok_embedding_hnsw`, cosine ops) exists and is used by the
planner (verified via `EXPLAIN`). It trades a small amount of recall for large
speedup — for a corpus this size (82,535 rows) the approximation error is
negligible in practice, but if you ever need exact nearest-neighbor guarantees,
force a sequential scan (`SET enable_indexscan = off` for that session) and
compare.

## Worked example

```python
from openai import OpenAI
import psycopg

query = "Why should I do karma without expecting result"
vec = OpenAI().embeddings.create(
    model="text-embedding-3-small", input=query, dimensions=1536
).data[0].embedding

with psycopg.connect(DSN) as conn, conn.cursor() as cur:
    cur.execute("""
        SELECT slok_id, section, author, content, score FROM (
            SELECT slok_id, section, author, content,
                   1 - (embedding <=> %(q)s::vector) AS score,
                   row_number() OVER (PARTITION BY slok_id ORDER BY embedding <=> %(q)s::vector) AS rn
            FROM slok_embedding
            WHERE lang = %(lang)s
        ) ranked
        WHERE rn = 1
        ORDER BY score DESC
        LIMIT %(k)s
    """, {"q": str(vec), "lang": "en", "k": 10})
    rows = cur.fetchall()
```

Confirmed against this query: top result `BG18.6` (0.5743), with `BG2.47` —
the canonical "you have a right to action, not its fruits" verse — appearing
at rank 6 (0.5230). Scores in the 0.50–0.57 range for a genuinely on-topic
query is the expected signal strength for this corpus (see Rule 4).
