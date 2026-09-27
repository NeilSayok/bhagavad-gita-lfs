// Local smoke test: `npx tsx --env-file=../../../.env test/localtest.ts <lang>:<character>`
process.env.GEMINI_API_KEY ??= process.env.GOOGLE_GENAI_API_KEY;
process.env.NEON_DATABASE_URL ??= process.env.NEON_POSTGRESQL_CONNECTION_STRING;

const verified = { uid: 'test', token: { email_verified: true } };

(async () => {
  const { askGita } = await import('../src/index.js');
  const [language, character] = (process.argv[2] ?? 'en:krishna').split(':');
  const query = process.argv[3] ?? 'Why should I do karma without expecting result';
  const authArg = process.argv[4] === 'unverified' ? { uid: 'x', token: { email_verified: false } } : verified;
  const t = Date.now();
  // @ts-ignore - minimal CallableRequest for .run()
  const res: any = await askGita.run({ data: { query, language, character }, auth: authArg, rawRequest: {}, acceptsStreaming: false });
  console.log(`--- ${language}/${character} (${Date.now() - t} ms) ---`);
  console.log(JSON.stringify(res, null, 2));
})().catch((e) => { console.error('ERROR:', e?.code ?? '', e?.message ?? e); process.exit(1); });
