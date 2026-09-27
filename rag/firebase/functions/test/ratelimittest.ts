// Rate limiter against the Firestore emulator:
//   firebase emulators:start --only firestore --project gitaapp-24519   (from rag/firebase)
//   FIRESTORE_EMULATOR_HOST=127.0.0.1:8080 GCLOUD_PROJECT=gitaapp-24519 npx tsx test/ratelimittest.ts
import { enforceRateLimit } from '../src/rateLimit';

if (!process.env.FIRESTORE_EMULATOR_HOST) throw new Error('refusing to run against production Firestore');

const tag = `ZZTEST-${Date.now()}`;
const attempt = async (uid: string, now?: number) => {
  try { await enforceRateLimit(uid, now); return 'ok'; }
  catch (e: any) { return `${e.code}:${e.details?.limit}:${e.details?.retryAfterSeconds}s`; }
};
const check = (name: string, pass: boolean, detail: string) =>
  console.log(`${pass ? 'PASS' : 'FAIL'}  ${name}  (${detail})`);

(async () => {
  // 1. burst: 5 per minute
  const t0 = Date.parse('2026-09-27T10:00:10Z');
  const burst = [];
  for (let i = 0; i < 6; i++) burst.push(await attempt(`${tag}-burst`, t0 + i * 100));
  check('6 sequential in one minute -> 5 ok, 6th rejected', burst.slice(0, 5).every((r) => r === 'ok') && burst[5].startsWith('resource-exhausted:minute'), burst[5]);

  // 2. window reset
  check('next minute -> allowed again', (await attempt(`${tag}-burst`, t0 + 60_000)) === 'ok', 'minute rolled over');

  // 3. concurrency: transaction must not let parallel calls all read "0 used"
  const par = await Promise.all(Array.from({ length: 10 }, () => attempt(`${tag}-par`, t0)));
  const okCount = par.filter((r) => r === 'ok').length;
  check('10 parallel -> exactly 5 ok', okCount === 5, `${okCount} ok`);

  // 4. daily cap: 50 spread over different minutes, 51st rejected
  const day: string[] = [];
  for (let i = 0; i < 51; i++) day.push(await attempt(`${tag}-day`, t0 + i * 60_000));
  const dayOk = day.filter((r) => r === 'ok').length;
  check('51 across the day -> 50 ok, 51st rejected (daily)', dayOk === 50 && day[50].startsWith('resource-exhausted:day'), day[50]);

  // 5. next UTC day resets
  check('next UTC day -> allowed again', (await attempt(`${tag}-day`, t0 + 86_400_000)) === 'ok', 'day rolled over');

  // 6. users are independent
  check('other user unaffected', (await attempt(`${tag}-other`, t0)) === 'ok', 'separate counter');
})();
