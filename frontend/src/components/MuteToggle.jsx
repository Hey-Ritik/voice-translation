import React from 'react';

const styles = {
  button: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 8,
    padding: '8px 14px',
    borderRadius: 'var(--radius)',
    border: '1px solid var(--border)',
    background: 'var(--surface)',
    color: 'var(--text-muted)',
    fontSize: 13,
    cursor: 'pointer',
  },
  active: {
    color: 'var(--accent)',
    borderColor: 'var(--accent)',
  },
};

export function MuteToggle({ muted, onToggle }) {
  return (
    <button
      type="button"
      style={{ ...styles.button, ...(muted ? {} : styles.active) }}
      onClick={onToggle}
      aria-label={muted ? 'Unmute TTS' : 'Mute TTS'}
    >
      {muted ? (
        <>
          <span aria-hidden>🔇</span>
          Sound off
        </>
      ) : (
        <>
          <span aria-hidden>🔊</span>
          Sound on
        </>
      )}
    </button>
  );
}
