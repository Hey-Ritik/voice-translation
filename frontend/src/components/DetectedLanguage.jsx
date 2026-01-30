import React from 'react';

const styles = {
  wrap: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 8,
    padding: '6px 12px',
    borderRadius: 20,
    background: 'var(--surface)',
    border: '1px solid var(--border)',
    fontSize: 13,
    color: 'var(--text-muted)',
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: '50%',
    background: 'var(--accent)',
  },
  dotInactive: {
    background: 'var(--text-muted)',
  },
};

export function DetectedLanguage({ label, active }) {
  return (
    <div style={styles.wrap}>
      <span style={{ ...styles.dot, ...(active ? {} : styles.dotInactive) }} />
      <span>Detected: {label || '—'}</span>
    </div>
  );
}
