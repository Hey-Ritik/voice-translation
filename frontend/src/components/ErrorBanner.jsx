import React from 'react';

const styles = {
  wrap: {
    padding: '12px 16px',
    borderRadius: 'var(--radius)',
    background: 'rgba(239, 68, 68, 0.15)',
    border: '1px solid rgba(239, 68, 68, 0.4)',
    color: '#fca5a5',
    fontSize: 14,
  },
};

export function ErrorBanner({ message }) {
  if (!message) return null;
  return <div style={styles.wrap} role="alert">{message}</div>;
}
