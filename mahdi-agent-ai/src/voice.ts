import type { Lang } from './types';

type SpeechRecognitionLike = {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  onresult: ((e: { resultIndex: number; results: ArrayLike<{ 0: { transcript: string }; isFinal: boolean }> }) => void) | null;
  onerror: ((e: { error: string }) => void) | null;
  onend: (() => void) | null;
  start(): void;
  stop(): void;
  abort(): void;
};

export const VOICE_LANGS = [
  { value: 'ar-SA', label: 'العربية (السعودية)' },
  { value: 'ar-EG', label: 'العربية (مصر)' },
  { value: 'en-US', label: 'English (US)' },
  { value: 'en-GB', label: 'English (UK)' },
  { value: 'fr-FR', label: 'Français' },
  { value: 'es-ES', label: 'Español' },
];

export function speechRecognitionCtor(): (new () => SpeechRecognitionLike) | null {
  const w = window as unknown as Record<string, unknown>;
  return ((w.SpeechRecognition ?? w.webkitSpeechRecognition) as (new () => SpeechRecognitionLike)) ?? null;
}

export const speechSupported = {
  input: () => speechRecognitionCtor() !== null,
  output: () => typeof window !== 'undefined' && 'speechSynthesis' in window,
};

/** Starts listening; `onText` receives interim and final transcripts. Returns a stop function. */
export function listen(
  voiceLang: string,
  onText: (text: string, isFinal: boolean) => void,
  onEnd: (error?: string) => void,
): () => void {
  const Ctor = speechRecognitionCtor();
  if (!Ctor) {
    onEnd('unsupported');
    return () => undefined;
  }
  const rec = new Ctor();
  rec.lang = voiceLang;
  rec.continuous = false;
  rec.interimResults = true;
  let finalText = '';
  rec.onresult = (e) => {
    let interim = '';
    for (let i = e.resultIndex; i < e.results.length; i++) {
      const r = e.results[i];
      if (r.isFinal) finalText += r[0].transcript;
      else interim += r[0].transcript;
    }
    onText((finalText + interim).trim(), false);
  };
  rec.onerror = (e) => onEnd(e.error);
  rec.onend = () => onEnd(undefined);
  rec.start();
  return () => {
    try {
      rec.stop();
    } catch {
      /* already stopped */
    }
  };
}

let currentUtterance: SpeechSynthesisUtterance | null = null;

export function speak(text: string, lang: Lang | 'auto' = 'auto', onDone?: () => void): void {
  if (!speechSupported.output()) return;
  stopSpeaking();
  const clean = text
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/[`*_#>[\]()]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 4000);
  if (!clean) return;
  const u = new SpeechSynthesisUtterance(clean);
  const isArabic = lang === 'ar' || (lang === 'auto' && /[\u0600-\u06FF]/.test(clean));
  u.lang = isArabic ? 'ar-SA' : 'en-US';
  u.rate = 1;
  u.onend = () => {
    currentUtterance = null;
    onDone?.();
  };
  u.onerror = () => {
    currentUtterance = null;
    onDone?.();
  };
  currentUtterance = u;
  window.speechSynthesis.speak(u);
}

export function stopSpeaking(): void {
  if (speechSupported.output()) window.speechSynthesis.cancel();
  currentUtterance = null;
}

export function isSpeaking(): boolean {
  return currentUtterance !== null || (speechSupported.output() && window.speechSynthesis.speaking);
}
