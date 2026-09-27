import { genkit, z } from 'genkit';
import { fallback, retry } from 'genkit/model/middleware';
import { googleAI } from '@genkit-ai/google-genai';
import { HttpsError, onCallGenkit } from 'firebase-functions/https';
import { defineSecret } from 'firebase-functions/params';
import { logger } from 'firebase-functions';

import { detectSearchLang, embedQuery, retrieveSloks } from './retrieve';
import { contextBlock, crisisSystemPrompt, languageRule, offTopicReply, systemPrompt } from './prompts';
import { CRISIS_FALLBACK, HELPLINES, helplineBlock, isSelfHarm } from './safety';
import { enforceRateLimit } from './rateLimit';

// googleAI() reads GEMINI_API_KEY from the environment; defineSecret exposes it there.
const geminiApiKey = defineSecret('GEMINI_API_KEY');
const openaiApiKey = defineSecret('OPENAI_API_KEY');
const neonDatabaseUrl = defineSecret('NEON_DATABASE_URL');

const ai = genkit({
  plugins: [googleAI()],
  model: googleAI.model('gemini-flash-latest'),
});

// gemini-flash-latest intermittently returns 503 "high demand". A user is waiting,
// so retry briefly, then fall back to the lighter model rather than failing.
const resilient = () => [
  retry({ maxRetries: 2, initialDelayMs: 500, maxDelayMs: 3000 }),
  fallback(ai, { models: [googleAI.model('gemini-flash-lite-latest')] }),
];

const SLOK_COUNT = 5;
const MAX_HISTORY = 6;

// Best-chunk cosine score below which an ENGLISH question has nothing to do with the
// Gita. Measured on English: off-topic tops out ~0.29, genuine personal questions go as
// low as 0.31, so 0.25 only drops obvious junk. Not applied to hi/be/ka: same-language
// scores there overlap completely (Bengali off-topic up to 0.44, on-topic from 0.36;
// Kannada "weather" 0.50 > Kannada "anger" 0.43), so no threshold is safe. Gemini's
// onTopic check covers those.
const MIN_RELEVANCE_EN = 0.25;

const LanguageSchema = z.enum(['en', 'hi', 'be', 'ka']);
const CharacterSchema = z.enum(['krishna', 'arjun']);

const AskGitaInput = z.object({
  query: z.string().trim().min(1).max(1000),
  character: CharacterSchema.default('krishna'),
  language: LanguageSchema.default('en'),
  history: z
    .array(
      z.object({
        role: z.enum(['user', 'model']),
        content: z.string().max(4000),
      }),
    )
    .default([]),
});

const AskGitaOutput = z.object({
  /** false = question was outside the Gita's scope; `answer` is a redirect, `sources` is []. */
  onTopic: z.boolean(),
  /** true = message expressed self-harm; `answer` is a supportive reply ending in helplines. */
  selfHarm: z.boolean(),
  answer: z.string(),
  language: LanguageSchema,
  character: CharacterSchema,
  sources: z.array(
    z.object({
      slokId: z.string(),
      chapter: z.number(),
      verse: z.number(),
      score: z.number(),
    }),
  ),
  /** Non-empty only when selfHarm is true, so the app can render tap-to-call buttons. */
  helplines: z.array(z.object({ name: z.string(), number: z.string(), note: z.string() })),
});

type Language = z.infer<typeof LanguageSchema>;
type Character = z.infer<typeof CharacterSchema>;
type History = { role: 'user' | 'model'; content: string }[];

const historyMessages = (history: History) =>
  history.slice(-MAX_HISTORY).map((m) => ({ role: m.role, content: [{ text: m.content }] }));

/** Supportive reply + code-appended helplines. Never fails: falls back to fixed text. */
async function crisisReply(query: string, character: Character, language: Language, history: History) {
  let text = CRISIS_FALLBACK[language];
  try {
    const { output } = await ai.generate({
      system: crisisSystemPrompt(character, language),
      messages: historyMessages(history),
      prompt: query,
      output: { schema: z.object({ answer: z.string() }) },
      use: resilient(),
    });
    if (output?.answer) text = output.answer;
  } catch (err) {
    logger.error('crisis reply generation failed, using fixed text', err);
  }
  return {
    onTopic: true,
    selfHarm: true,
    answer: `${text}\n\n${helplineBlock(language)}`,
    language,
    character,
    sources: [],
    helplines: HELPLINES,
  };
}

const askGitaFlow = ai.defineFlow(
  {
    name: 'askGita',
    inputSchema: AskGitaInput,
    outputSchema: AskGitaOutput,
  },
  // Genkit validates against inputSchema but passes the original object through, so
  // zod .default() values are not applied -- default omitted fields here instead.
  async ({ query, character = 'krishna', language = 'en', history = [] }, { context }) => {
    const uid = context?.auth?.uid as string | undefined;
    if (!uid) throw new HttpsError('unauthenticated', 'Sign in to ask a question.');

    // 1. Self-harm first, and before the rate limit: someone in crisis must never be
    //    told to try again later. Moderation is free, so skipping the limit costs nothing.
    if (await isSelfHarm(openaiApiKey.value(), query)) {
      return crisisReply(query, character, language, history);
    }

    // 2. Rate limit before anything that costs money.
    await enforceRateLimit(uid);

    // 3. Retrieve in the language the question is written in; slok text is English.
    const searchLang = detectSearchLang(query);
    const vector = await embedQuery(openaiApiKey.value(), query);
    const sloks = await retrieveSloks(
      neonDatabaseUrl.value(),
      vector,
      searchLang,
      SLOK_COUNT,
      searchLang === 'en' ? MIN_RELEVANCE_EN : undefined,
    );

    // 4. English score gate: obvious junk never reaches Gemini.
    if (searchLang === 'en' && !sloks.length) {
      return {
        onTopic: false,
        selfHarm: false,
        answer: offTopicReply(character, language),
        language,
        character,
        sources: [],
        helplines: [],
      };
    }

    // 5. One Gemini call decides self-harm and scope, then answers.
    const { output } = await ai.generate({
      system: systemPrompt(character, language),
      messages: historyMessages(history),
      prompt: `${contextBlock(sloks)}\n\n<question>\n${query}\n</question>\n\n${languageRule(language)}`,
      // Flags first, so the model commits to both decisions before writing.
      output: {
        schema: z.object({ selfHarm: z.boolean(), onTopic: z.boolean(), answer: z.string() }),
      },
      use: resilient(),
    });
    if (!output) throw new Error('model returned no structured output');

    // Moderation misses Kannada and indirect phrasing; Gemini caught it instead.
    if (output.selfHarm) {
      return {
        onTopic: true,
        selfHarm: true,
        answer: `${output.answer}\n\n${helplineBlock(language)}`,
        language,
        character,
        sources: [],
        helplines: HELPLINES,
      };
    }

    return {
      onTopic: output.onTopic,
      selfHarm: false,
      answer: output.answer,
      language,
      character,
      sources: !output.onTopic
        ? []
        : sloks.map(({ slokId, chapter, verse, score }) => ({
            slokId,
            chapter,
            verse,
            score: Math.round(score * 10000) / 10000,
          })),
      helplines: [],
    };
  },
);

// Not hasClaim('email_verified') as in the Genkit doc: hasClaim only checks the claim
// *exists*, and every Firebase ID token carries email_verified (true or false), so it
// admits unverified users. hasClaim's value param is typed string, so it can't match
// the boolean either. Check the value directly.
const emailVerified = (auth: { token: Record<string, unknown> } | null) =>
  auth?.token.email_verified === true;

export const askGita = onCallGenkit(
  {
    // Next to Firestore (asia-south1) and near Neon (ap-southeast-1) and the users;
    // the default us-central1 would add Pacific round-trips to every request.
    region: 'asia-south1',
    secrets: [geminiApiKey, openaiApiKey, neonDatabaseUrl],
    authPolicy: emailVerified,
    enforceAppCheck: true,
  },
  askGitaFlow,
);
