import React, { useEffect, useRef } from 'react';

const styles = {
  panels: {
    flex: 1,
    minHeight: 0,
    display: 'grid',
    gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)',
    gap: 16,
    padding: 16,
    overflow: 'hidden',
  },
  panel: {
    display: 'flex',
    flexDirection: 'column',
    minHeight: 0,
    borderRadius: 'var(--radius)',
    border: '1px solid var(--border)',
    background: 'var(--bg)',
    overflow: 'hidden',
  },
  panelHeader: {
    padding: '8px 12px',
    borderBottom: '1px solid var(--border)',
    fontSize: 11,
    fontWeight: 600,
    color: 'var(--text-muted)',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
  },
  scroll: {
    flex: 1,
    overflowY: 'auto',
    padding: 12,
    display: 'flex',
    flexDirection: 'column',
    gap: 8,
    justifyContent: 'flex-end',
  },
  line: {
    fontSize: 16,
    lineHeight: 1.4,
    color: 'var(--text)',
  },
  lineTranslated: {
    fontSize: 16,
    lineHeight: 1.4,
    color: 'var(--text-muted)',
    fontStyle: 'italic',
  },
  empty: {
    color: 'var(--text-muted)',
    fontSize: 13,
    textAlign: 'center',
    padding: 16,
  },
};

export function CaptionDisplay({ captions }) {
  const origScrollRef = useRef(null);
  const transScrollRef = useRef(null);

  useEffect(() => {
    [origScrollRef, transScrollRef].forEach((ref) => {
      const el = ref.current;
      if (el) el.scrollTop = el.scrollHeight;
    });
  }, [captions]);

  const originals = captions.map((c) => c.original).filter(Boolean);
  const translated = captions.map((c) => c.translated).filter(Boolean);
  const hasAny = originals.length > 0 || translated.length > 0;

  return (
    <div className="caption-panels" style={styles.panels}>
      <div style={styles.panel}>
        <div style={styles.panelHeader}>Live speech (original)</div>
        <div ref={origScrollRef} style={styles.scroll}>
          {originals.length === 0 && (
            <div style={styles.empty}>What you say appears here.</div>
          )}
          {originals.map((text, i) => (
            <div key={i} style={styles.line}>
              {text}
            </div>
          ))}
        </div>
      </div>
      <div style={styles.panel}>
        <div style={styles.panelHeader}>Translation</div>
        <div ref={transScrollRef} style={styles.scroll}>
          {translated.length === 0 && (
            <div style={styles.empty}>Translated text appears here.</div>
          )}
          {translated.map((text, i) => (
            <div key={i} style={styles.lineTranslated}>
              {text}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
