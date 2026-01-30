import { useCallback, useRef, useState } from 'react';

const SAMPLE_RATE = 16000;
const CHUNK_MS = 2000;
const CHUNK_SAMPLES = (SAMPLE_RATE * CHUNK_MS) / 1000;

/**
 * Capture microphone and emit raw PCM chunks (16-bit mono) at fixed intervals.
 * Uses ScriptProcessorNode for chunked capture (deprecated but widely supported).
 * Fallback: MediaRecorder with webm, then we'd need to decode on backend or use different pipeline.
 * For Whisper we need raw PCM 16kHz mono. So we use AudioContext with resampling or
 * request 16kHz from getUserMedia if supported. Actually browsers typically give 44.1k/48k.
 * We'll send chunks at 16kHz equivalent size: record at context.sampleRate, then
 * in backend we pass sample_rate from frontend so Whisper can handle.
 */
export function useAudioStream({ onChunk, onError }) {
  const [isRecording, setIsRecording] = useState(false);
  const [micError, setMicError] = useState(null);
  const streamRef = useRef(null);
  const contextRef = useRef(null);
  const processorRef = useRef(null);
  const sourceRef = useRef(null);
  const bufferRef = useRef([]);
  const targetSamplesRef = useRef(0);

  const start = useCallback(async () => {
    setMicError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const context = new (window.AudioContext || window.webkitAudioContext)({
        sampleRate: SAMPLE_RATE,
      });
      contextRef.current = context;
      const source = context.createMediaStreamSource(stream);
      sourceRef.current = source;

      // Buffer enough samples for CHUNK_MS at context sample rate
      const contextChunkSamples = Math.ceil((context.sampleRate * CHUNK_MS) / 1000);
      targetSamplesRef.current = contextChunkSamples;
      bufferRef.current = [];

      const processor = context.createScriptProcessor(4096, 1, 1);
      processor.onaudioprocess = (e) => {
        if (!streamRef.current) return;
        const input = e.inputBuffer.getChannelData(0);
        for (let i = 0; i < input.length; i++) {
          bufferRef.current.push(input[i]);
        }
        while (bufferRef.current.length >= contextChunkSamples) {
          const chunk = bufferRef.current.splice(0, contextChunkSamples);
          const pcm16 = new Int16Array(chunk.length);
          for (let i = 0; i < chunk.length; i++) {
            const s = Math.max(-1, Math.min(1, chunk[i]));
            pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
          }
          const blob = new Blob([pcm16.buffer]);
          const reader = new FileReader();
          reader.onloadend = () => {
            const base64 = btoa(
              new Uint8Array(reader.result).reduce((acc, b) => acc + String.fromCharCode(b), '')
            );
            onChunk?.(base64, context.sampleRate);
          };
          reader.readAsArrayBuffer(blob);
        }
      };
      processor.connect(context.destination);
      processorRef.current = processor;
      source.connect(processor);
      setIsRecording(true);
    } catch (err) {
      const msg = err.name === 'NotAllowedError'
        ? 'Microphone access denied'
        : err.name === 'NotFoundError'
          ? 'No microphone found'
          : err.message || 'Failed to access microphone';
      setMicError(msg);
      onError?.(msg);
    }
  }, [onChunk, onError]);

  const stop = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    if (processorRef.current && sourceRef.current && contextRef.current) {
      try {
        sourceRef.current.disconnect();
        processorRef.current.disconnect();
      } catch (_) {}
      processorRef.current = null;
      sourceRef.current = null;
    }
    if (contextRef.current) {
      contextRef.current.close().catch(() => {});
      contextRef.current = null;
    }
    bufferRef.current = [];
    setIsRecording(false);
  }, []);

  return { start, stop, isRecording, micError };
}
