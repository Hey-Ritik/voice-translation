import React, { useCallback, useEffect, useRef, useState } from 'react';
import { CaptionDisplay } from './components/CaptionDisplay';
import { ClearButton } from './components/ClearButton';
import { DetectedLanguage } from './components/DetectedLanguage';
import { ErrorBanner } from './components/ErrorBanner';
import { LanguageSelector } from './components/LanguageSelector';
import { MicButton } from './components/MicButton';
import { MuteToggle } from './components/MuteToggle';
import { SpeakingIndicator } from './components/SpeakingIndicator';
import { AUTO_CLEAR_MS, MAX_CAPTION_LINES, SILENCE_CLEAR_MS } from './constants/captionConfig';
import { useAudioStream } from './hooks/useAudioStream';
import { useTranslationSocket } from './hooks/useTranslationSocket';
import { useTTS } from './hooks/useTTS';
import { Footer } from './components/Footer';

const appStyles = {
  root: {
    minHeight: '100%',
    display: 'flex',
    flexDirection: 'column',
    maxWidth: 800,
    margin: '0 auto',
    padding: 24,
  },
  header: {
    marginBottom: 24,
    display: 'flex',
    flexDirection: 'column',
    gap: 8,
  },
  title: {
    fontSize: 24,
    fontWeight: 700,
    color: 'var(--text)',
    margin: 0,
  },
  subtitle: {
    fontSize: 14,
    color: 'var(--text-muted)',
    margin: 0,
  },
  controls: {
    display: 'flex',
    flexWrap: 'wrap',
    alignItems: 'flex-end',
    gap: 24,
    marginBottom: 16,
  },
  captionsSection: {
    flex: 1,
    minHeight: 280,
    display: 'flex',
    flexDirection: 'column',
    borderRadius: 'var(--radius)',
    border: '1px solid var(--border)',
    background: 'var(--surface)',
    overflow: 'hidden',
  },
  statusBar: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    flexWrap: 'wrap',
    gap: 12,
    padding: '12px 16px',
    borderBottom: '1px solid var(--border)',
    background: 'var(--bg)',
    fontSize: 13,
    color: 'var(--text-muted)',
  },
  micSection: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: 12,
    padding: 24,
    borderBottom: '1px solid var(--border)',
  },
};

export default function App() {
  const [targetLang, setTargetLang] = useState('hi');
  const [captions, setCaptions] = useState([]);
  const [detectedLang, setDetectedLang] = useState(null);
  const [detectedLangDisplay, setDetectedLangDisplay] = useState('—');
  const [error, setError] = useState(null);
  const [muted, setMuted] = useState(false);
  const lastCaptionTimeRef = useRef(0);
  const lastSpokenRef = useRef('');
  const autoClearTimerRef = useRef(null);

  const { speak, isSpeaking } = useTTS(targetLang, muted);

  const clearCaptions = useCallback(() => {
    setCaptions([]);
  }, []);

  const onCaption = useCallback(
    (data) => {
      if (data.error) {
        setError(data.error);
        return;
      }
      setError(null);
      if (data.detected_lang_display) setDetectedLangDisplay(data.detected_lang_display);
      if (data.detected_lang != null) setDetectedLang(data.detected_lang);
      if (!data.original && !data.translated) return;
      const original = (data.original || '').trim();
      const translated = (data.translated || '').trim();
      if (!original && !translated) return;
      const now = Date.now();
      setCaptions((prev) => {
        const last = prev[prev.length - 1];
        if (last && last.original === original && last.translated === translated) return prev;
        if (now - lastCaptionTimeRef.current > SILENCE_CLEAR_MS) {
          lastCaptionTimeRef.current = now;
          const next = [{ original, translated }];
          return next.slice(-MAX_CAPTION_LINES);
        }
        lastCaptionTimeRef.current = now;
        const next = [...prev, { original, translated }];
        return next.slice(-MAX_CAPTION_LINES);
      });
      if (translated && !muted && translated !== lastSpokenRef.current) {
        lastSpokenRef.current = translated;
        speak(translated);
      }
    },
    [muted, speak]
  );

  const {
    connect,
    disconnect,
    sendChunk,
    connected,
    socketError,
  } = useTranslationSocket({
    onCaption,
    onError: (msg) => setError((e) => msg || e),
    onReady: () => setError(null),
  });

  const onChunk = useCallback(
    (base64, sampleRate) => {
      sendChunk(base64, targetLang, sampleRate);
    },
    [sendChunk, targetLang]
  );

  const { start: startMic, stop: stopMic, isRecording, micError } = useAudioStream({
    onChunk,
    onError: (msg) => setError((e) => msg || e),
  });

  const pendingStartRef = useRef(false);

  const handleStart = useCallback(() => {
    setError(null);
    if (connected) {
      startMic();
      return;
    }
    pendingStartRef.current = true;
    connect();
  }, [connected, connect, startMic]);

  useEffect(() => {
    if (connected && pendingStartRef.current) {
      pendingStartRef.current = false;
      startMic();
    }
  }, [connected, startMic]);

  const handleStop = useCallback(() => {
    stopMic();
    clearCaptions();
  }, [stopMic, clearCaptions]);

  useEffect(() => {
    clearCaptions();
  }, [targetLang, clearCaptions]);

  useEffect(() => {
    autoClearTimerRef.current = setInterval(() => {
      setCaptions((prev) => {
        if (prev.length === 0) return prev;
        const now = Date.now();
        if (now - lastCaptionTimeRef.current >= AUTO_CLEAR_MS) {
          return [];
        }
        return prev;
      });
    }, 2000);
    return () => {
      if (autoClearTimerRef.current) clearInterval(autoClearTimerRef.current);
    };
  }, []);

  const displayError = error || micError || (connected ? null : socketError);

  return (
    <div style={appStyles.root}>
      <header style={appStyles.header}>
        <h1 style={appStyles.title}>Voice Translation</h1>
        <p style={appStyles.subtitle}>
          Real-time captions and translation. Speak in any language; see original and target text.
        </p>
      </header>

      {displayError && <ErrorBanner message={displayError} />}

      <div style={appStyles.controls}>
        <LanguageSelector
          value={targetLang}
          onChange={setTargetLang}
          disabled={isRecording}
        />
        <DetectedLanguage label={detectedLangDisplay} active={isRecording || !!detectedLang} />
        <MuteToggle muted={muted} onToggle={() => setMuted((m) => !m)} />
        <ClearButton onClick={clearCaptions} disabled={false} />
      </div>

      <section style={appStyles.captionsSection}>
        <div style={appStyles.statusBar}>
          <span>
            {connected ? 'Connected' : 'Click Start to connect'} • Target: {targetLang}
          </span>
          <SpeakingIndicator isSpeaking={isSpeaking} />
        </div>
        <CaptionDisplay captions={captions} />
        <div style={appStyles.micSection}>
          <MicButton
            isRecording={isRecording}
            onStart={handleStart}
            onStop={handleStop}
            disabled={false}
          />
          <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>
            {isRecording ? 'Listening…' : 'Click to start microphone'}
          </span>
        </div>
      </section>
      <Footer />
    </div>
  );
}
