import { neon } from '@neondatabase/serverless';
import OpenAI from 'openai';

// Must match how slok_embedding was built (rag/build_rag.py): same model, same width.
const EMBED_MODEL = 'text-embedding-3-small';
const EMBED_DIMENSIONS = 1536;

export type SearchLang = 'en' | 'hi' | 'be' | 'ka';

const SLOK_TEXT_BASE = 'https://neilsayok.github.io/bhagavad-gita-lfs/rag/slok';

// Unicode blocks for the scripts the corpus is embedded in. (Sanskrit shares
// Devanagari with Hindi; a Devanagari question is searched against Hindi.)
const SCRIPTS: [SearchLang, RegExp][] = [
  ['hi', /[ऀ-ॿ]/g],
  ['be', /[ঀ-৿]/g],
  ['ka', /[ಀ-೿]/g],
];

/**
 * Which language's vectors to search, from the script the question is written in --
 * not the user's language setting. Searching a Kannada question against English
 * vectors scores unusably (Kannada "control anger" 0.154 < Kannada "weather" 0.302,
 * some queries return no rows); against Kannada vectors it scores normally.
 * Latin script (including romanized Hindi) searches English.
 */
export function detectSearchLang(query: string): SearchLang {
  let best: SearchLang = 'en';
  let bestCount = 0;
  for (const [lang, re] of SCRIPTS) {
    const count = query.match(re)?.length ?? 0;
    if (count > bestCount) [best, bestCount] = [lang, count];
  }
  const latin = query.match(/[A-Za-z]/g)?.length ?? 0;
  return bestCount > latin ? best : 'en';
}

// Over-fetch chunks, then dedupe to distinct sloks in code. A window-function dedupe
// in SQL would compute distance for every English row and bypass the HNSW index.
const CANDIDATE_CHUNKS = 40;
const COMMENTARIES_PER_SLOK = 2;

export interface Commentary {
  author: string;
  content: string;
}

export interface RetrievedSlok {
  slokId: string;
  chapter: number;
  verse: number;
  score: number;
  /** Speaker, verse, word meanings, life application — everything before the commentaries. */
  core: string;
  /** Commentary chunks that actually matched the query, best first. */
  commentary: Commentary[];
}

interface ChunkRow {
  slok_id: string;
  section: string;
  author: string | null;
  content: string;
  score: number;
}

export async function embedQuery(apiKey: string, query: string): Promise<number[]> {
  const openai = new OpenAI({ apiKey });
  const res = await openai.embeddings.create({
    model: EMBED_MODEL,
    input: query,
    dimensions: EMBED_DIMENSIONS,
  });
  return res.data[0].embedding;
}

function parseSlokId(slokId: string): { chapter: number; verse: number } {
  const m = /^BG(\d+)\.(\d+)$/.exec(slokId);
  if (!m) throw new Error(`unexpected slok_id: ${slokId}`);
  return { chapter: Number(m[1]), verse: Number(m[2]) };
}

/** Everything before the first "Commentary by" header; commentaries come from Neon instead. */
function trimToCore(text: string): string {
  const cut = text.search(/^Commentary by /m);
  return (cut === -1 ? text : text.slice(0, cut)).trim();
}

// Slok text for the prompt is always English, whatever language was searched;
// Gemini writes the answer in the user's language.
async function fetchCore(chapter: number, verse: number): Promise<string> {
  const url = `${SLOK_TEXT_BASE}/en/plain_chapter_${chapter}_slok_${verse}.txt`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`fetch ${url} failed: ${res.status}`);
  return trimToCore(await res.text());
}

/**
 * Top `limit` distinct sloks in `lang`. When `minScore` is given, returns [] if even the
 * best chunk scores below it (question unrelated to the Gita) -- checked before any slok
 * text is fetched. Pass it only where a threshold has been calibrated.
 */
export async function retrieveSloks(
  databaseUrl: string,
  vector: number[],
  lang: SearchLang,
  limit: number,
  minScore?: number,
): Promise<RetrievedSlok[]> {
  const sql = neon(databaseUrl);
  const q = JSON.stringify(vector);

  // relaxed_order lets HNSW keep scanning past ef_search when the lang filter
  // discards candidates, so a query can never come back short of rows.
  // ef_search 100 (default 40): at 40 the approximate search dropped the true best
  // match (BG18.6 for the karma query); 100 matched an exact brute-force scan.
  const [, , rows] = (await sql.transaction([
    sql`SET LOCAL hnsw.iterative_scan = relaxed_order`,
    sql`SET LOCAL hnsw.ef_search = 100`,
    sql`SELECT slok_id, section, author, content,
               1 - (embedding <=> ${q}::vector) AS score
        FROM slok_embedding
        WHERE lang = ${lang}
        ORDER BY embedding <=> ${q}::vector
        LIMIT ${CANDIDATE_CHUNKS}`,
  ])) as [unknown, unknown, ChunkRow[]];

  // relaxed_order may return slightly out of order; re-sort before grouping.
  rows.sort((a, b) => Number(b.score) - Number(a.score));
  if (!rows.length) return [];
  if (minScore !== undefined && Number(rows[0].score) < minScore) return [];

  const bySlok = new Map<string, { score: number; commentary: Commentary[] }>();
  for (const row of rows) {
    let entry = bySlok.get(row.slok_id);
    if (!entry) {
      if (bySlok.size >= limit) continue;
      entry = { score: Number(row.score), commentary: [] };
      bySlok.set(row.slok_id, entry);
    }
    if (row.section === 'commentary' && row.author && entry.commentary.length < COMMENTARIES_PER_SLOK) {
      entry.commentary.push({ author: row.author, content: row.content });
    }
  }

  return Promise.all(
    [...bySlok].map(async ([slokId, { score, commentary }]) => {
      const { chapter, verse } = parseSlokId(slokId);
      return { slokId, chapter, verse, score, commentary, core: await fetchCore(chapter, verse) };
    }),
  );
}
