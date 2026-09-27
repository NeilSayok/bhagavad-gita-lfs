// End-to-end limit + crisis bypass through askGita, against the Firestore emulator.
//   FIRESTORE_EMULATOR_HOST=127.0.0.1:8080 GCLOUD_PROJECT=gitaapp-24519 \
//     npx tsx --env-file=../../../.env test/flowlimittest.ts
process.env.GEMINI_API_KEY ??= process.env.GOOGLE_GENAI_API_KEY;
process.env.NEON_DATABASE_URL ??= process.env.NEON_POSTGRESQL_CONNECTION_STRING;
if (!process.env.FIRESTORE_EMULATOR_HOST) throw new Error('refusing to run against production Firestore');

(async () => {
  const mod: any = await import('../src/index.js');
  const askGita = mod.askGita ?? mod.default?.askGita;
  const { enforceRateLimit } = await import('../src/rateLimit.js') as any;
  const uid = `ZZTEST-flow-${Date.now()}`;
  const call = (query: string) => askGita.run({ data: { query }, auth: { uid, token: { email_verified: true } }, rawRequest: {}, acceptsStreaming: false });

  for (let i = 0; i < 5; i++) await enforceRateLimit(uid);   // use up this minute
  console.log('limit exhausted for', uid);

  const t = Date.now();
  try { await call('How do I control anger?'); console.log('FAIL  normal question was answered despite limit'); }
  catch (e: any) { console.log(`${e.code === 'resource-exhausted' ? 'PASS' : 'FAIL'}  normal question -> ${e.code} in ${Date.now() - t} ms (fast = no embedding/Gemini call)`); }

  const r = await call('I want to end my life, nothing matters anymore');
  console.log(`${r.selfHarm && r.helplines.length ? 'PASS' : 'FAIL'}  crisis message while limited -> selfHarm=${r.selfHarm}, helplines=${r.helplines.length}`);
  console.log('      ' + r.answer.split('\n')[0].slice(0, 160));
})().catch((e) => { console.error('ERROR', e?.code, e?.message); process.exit(1); });
