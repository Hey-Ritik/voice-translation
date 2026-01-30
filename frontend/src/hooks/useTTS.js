/**
 * Text-to-speech using Web Speech API (SpeechSynthesis).
 * Auto-plays translated text in target language; supports mute and speaking indicator.
 */
import { useCallback, useEffect, useRef, useState } from 'react';

// Map our language codes to Web Speech API locale (e.g. hi -> hi-IN)
const LANG_TO_LOCALE = {
  hi: 'hi-IN',
  bn: 'bn-IN',
  ta: 'ta-IN',
  te: 'te-IN',
  mr: 'mr-IN',
  ur: 'ur-PK',
  pa: 'pa-IN',
  gu: 'gu-IN',
  kn: 'kn-IN',
  ml: 'ml-IN',
  en: 'en-US',
  zh: 'zh-CN',
  fr: 'fr-FR',
  de: 'de-DE',
  es: 'es-ES',
  ar: 'ar-SA',
  ja: 'ja-JP',
  ko: 'ko-KR',
  ru: 'ru-RU',
  pt: 'pt-BR',
  it: 'it-IT',
  th: 'th-TH',
  vi: 'vi-VN',
  id: 'id-ID',
  tr: 'tr-TR',
};

export function useTTS(targetLang, muted) {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const utteranceRef = useRef(null);
  const mountedRef = useRef(true);

  const speak = useCallback(
    (text) => {
      if (!text || typeof text !== 'string' || !text.trim()) return;
      if (muted) return;
      if (typeof window === 'undefined' || !window.speechSynthesis) return;

      window.speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(text.trim());
      u.lang = LANG_TO_LOCALE[targetLang] || targetLang || 'en-US';
      u.rate = 1.0;
      u.onstart = () => {
        if (mountedRef.current) setIsSpeaking(true);
      };
      u.onend = () => {
        if (mountedRef.current) setIsSpeaking(false);
      };
      u.onerror = () => {
        if (mountedRef.current) setIsSpeaking(false);
      };
      utteranceRef.current = u;
      window.speechSynthesis.speak(u);
    },
    [targetLang, muted]
  );

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      if (typeof window !== 'undefined' && window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  return { speak, isSpeaking };
}
