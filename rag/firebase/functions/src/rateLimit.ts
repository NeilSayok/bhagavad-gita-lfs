import { getApps, initializeApp } from 'firebase-admin/app';
import { getFirestore } from 'firebase-admin/firestore';
import { HttpsError } from 'firebase-functions/https';

// Burst limit stops scripted hammering; daily limit caps OpenAI + Gemini spend per account.
const PER_MINUTE = 5;
const PER_DAY = 50;

const MINUTE_MS = 60_000;
const DAY_MS = 86_400_000;

interface Usage {
  minute: number; // index of the fixed 1-minute window the count belongs to
  minuteCount: number;
  day: number; // index of the fixed UTC day
  dayCount: number;
}

function db() {
  if (!getApps().length) initializeApp();
  return getFirestore();
}

/**
 * Count one request for `uid`, or throw `resource-exhausted` if either window is full.
 * Runs in a transaction so two concurrent requests can't both read "4 of 5" and pass.
 * A rejected request is not counted.
 */
export async function enforceRateLimit(uid: string, now = Date.now()): Promise<void> {
  const ref = db().collection('rateLimits').doc(uid);
  const minute = Math.floor(now / MINUTE_MS);
  const day = Math.floor(now / DAY_MS);

  await db().runTransaction(async (tx) => {
    const prev = (await tx.get(ref)).data() as Usage | undefined;
    const minuteCount = prev?.minute === minute ? prev.minuteCount : 0;
    const dayCount = prev?.day === day ? prev.dayCount : 0;

    if (dayCount >= PER_DAY) {
      const retryAfterSeconds = Math.ceil(((day + 1) * DAY_MS - now) / 1000);
      throw new HttpsError('resource-exhausted', `Daily limit of ${PER_DAY} questions reached.`, {
        limit: 'day',
        retryAfterSeconds,
      });
    }
    if (minuteCount >= PER_MINUTE) {
      const retryAfterSeconds = Math.ceil(((minute + 1) * MINUTE_MS - now) / 1000);
      throw new HttpsError('resource-exhausted', 'Too many questions, please wait a moment.', {
        limit: 'minute',
        retryAfterSeconds,
      });
    }

    tx.set(ref, { minute, minuteCount: minuteCount + 1, day, dayCount: dayCount + 1 } satisfies Usage);
  });
}
