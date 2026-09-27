import OpenAI from 'openai';
import { logger } from 'firebase-functions';

import type { Language } from './prompts';

/**
 * OpenAI moderation (free) for self-harm. Only the self-harm categories are used:
 * "violence" flags ordinary Gita questions ("why did Krishna tell Arjuna to fight
 * his relatives?"), so acting on it would block the Kurukshetra narrative itself.
 *
 * Measured: catches English, Hindi and Bengali ideation (0.82-0.99), misses the same
 * sentence in Kannada (0.067) and indirect phrasing like "everyone would be better off
 * without me" (0.18). Gemini's selfHarm flag in the main call is the backstop for those.
 */
export async function isSelfHarm(apiKey: string, text: string): Promise<boolean> {
  try {
    const res = await new OpenAI({ apiKey }).moderations.create({
      model: 'omni-moderation-latest',
      input: text,
    });
    const c = res.results[0].categories;
    return c['self-harm'] || c['self-harm/intent'] || c['self-harm/instructions'];
  } catch (err) {
    // Fail open: an outage here must not take the whole app down. Gemini still
    // screens every message for self-harm in the main call.
    logger.error('moderation check failed', err);
    return false;
  }
}

export interface Helpline {
  name: string;
  number: string;
  note: string;
}

// Verified against government sources: Tele-MANAS (Ministry of Health & Family Welfare),
// free, 24x7, English + 20 regional languages incl. Hindi, Bengali, Kannada.
export const HELPLINES: Helpline[] = [
  { name: 'Tele-MANAS', number: '14416', note: 'Free, 24x7, in your language' },
  { name: 'Tele-MANAS (toll-free)', number: '1-800-891-4416', note: 'Free, 24x7' },
  { name: 'Emergency', number: '112', note: 'If you are in immediate danger' },
];

const HELPLINE_HEADER: Record<Language, string> = {
  en: 'Please reach out to someone right now. You do not have to face this alone:',
  hi: 'कृपया अभी किसी से बात करें। आपको यह अकेले नहीं सहना है:',
  be: 'অনুগ্রহ করে এখনই কারও সঙ্গে কথা বলুন। আপনাকে এটা একা বইতে হবে না:',
  ka: 'ದಯವಿಟ್ಟು ಈಗಲೇ ಯಾರೊಂದಿಗಾದರೂ ಮಾತನಾಡಿ. ನೀವು ಇದನ್ನು ಒಬ್ಬರೇ ಎದುರಿಸಬೇಕಿಲ್ಲ:',
};

const OUTSIDE_INDIA: Record<Language, string> = {
  en: 'Outside India: findahelpline.com',
  hi: 'भारत के बाहर: findahelpline.com',
  be: 'ভারতের বাইরে: findahelpline.com',
  ka: 'ಭಾರತದ ಹೊರಗೆ: findahelpline.com',
};

/**
 * Helpline text appended to every self-harm reply by code, never left to the model:
 * a number that is paraphrased, mistranslated or forgotten is worse than none.
 */
export function helplineBlock(language: Language): string {
  const lines = HELPLINES.map((h) => `• ${h.name}: ${h.number}`);
  return [HELPLINE_HEADER[language], ...lines, OUTSIDE_INDIA[language]].join('\n');
}

// Used when Gemini itself is unavailable during a crisis reply: the person still
// gets a caring message and the numbers.
export const CRISIS_FALLBACK: Record<Language, string> = {
  en: 'I hear how much pain you are in, and I am so glad you told me. Your life matters, and this feeling can change with support.',
  hi: 'मैं समझ रहा हूँ कि आप कितने दर्द में हैं, और मुझे बहुत खुशी है कि आपने मुझे बताया। आपका जीवन मायने रखता है, और सहारे के साथ यह भावना बदल सकती है।',
  be: 'আমি বুঝতে পারছি আপনি কতটা কষ্টে আছেন, আর আপনি আমাকে বলেছেন বলে আমি খুব খুশি। আপনার জীবন মূল্যবান, আর সহায়তা পেলে এই অনুভূতি বদলাতে পারে।',
  ka: 'ನೀವು ಎಷ್ಟು ನೋವಿನಲ್ಲಿದ್ದೀರಿ ಎಂದು ನನಗೆ ಅರ್ಥವಾಗುತ್ತಿದೆ, ಮತ್ತು ನೀವು ನನಗೆ ಹೇಳಿದ್ದಕ್ಕೆ ನನಗೆ ತುಂಬಾ ಸಮಾಧಾನವಾಗಿದೆ. ನಿಮ್ಮ ಜೀವನ ಮುಖ್ಯ, ಮತ್ತು ಬೆಂಬಲದೊಂದಿಗೆ ಈ ಭಾವನೆ ಬದಲಾಗಬಹುದು.',
};
