import React from 'react';

const styles = {
  button: {
    padding: '8px 14px',
    borderRadius: 'var(--radius)',
    border: '1px solid var(--border)',
    background: 'var(--surface)',
    color: 'var(--text-muted)',
    fontSize: 13,
    cursor: 'pointer',
  },
};

export function ClearButton({ onClick, disabled }) {
  return (
    <button type="button" style={styles.button} onClick={onClick} disabled={disabled}>
      Clear
    </button>
  );
}
