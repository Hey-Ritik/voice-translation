import { useCallback, useEffect, useRef, useState } from 'react';

const getWsUrl = () => {
  const base = import.meta.env.VITE_WS_URL || '';
  if (base) return base;
  const { protocol, host } = window.location;
  const wsProtocol = protocol === 'https:' ? 'wss:' : 'ws:';
  return `${wsProtocol}//${host}/ws/audio`;
};

export function useTranslationSocket({ onCaption, onError, onReady }) {
  const [connected, setConnected] = useState(false);
  const [socketError, setSocketError] = useState(null);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    const url = getWsUrl();
    setSocketError(null);
    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;
      ws.onopen = () => {
        setConnected(true);
        setSocketError(null);
      };
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'ready') {
            onReady?.(data);
          } else if (data.type === 'caption') {
            onCaption?.(data);
          } else if (data.type === 'error') {
            onError?.(data.error);
          }
        } catch (_) {
          onError?.('Invalid server response');
        }
      };
      const connectionFailedMsg = 'Cannot connect to backend. Start it first: in the project folder run "cd backend" then "uvicorn app.main:app --port 8000" (see README).';
      ws.onerror = () => {
        setSocketError(connectionFailedMsg);
      };
      ws.onclose = (event) => {
        setConnected(false);
        wsRef.current = null;
        if (event.code !== 1000 && event.code !== 1001 && !event.wasClean) {
          setSocketError(connectionFailedMsg);
        }
      };
    } catch (err) {
      setSocketError(err.message || 'Failed to connect');
      setConnected(false);
    }
  }, [onCaption, onError, onReady]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setConnected(false);
  }, []);

  const sendChunk = useCallback((audioBase64, targetLang, sampleRate = 16000) => {
    if (wsRef.current?.readyState !== WebSocket.OPEN) return;
    wsRef.current.send(
      JSON.stringify({
        audio: audioBase64,
        target_lang: targetLang,
        sample_rate: sampleRate,
      })
    );
  }, []);

  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return { connect, disconnect, sendChunk, connected, socketError };
}
