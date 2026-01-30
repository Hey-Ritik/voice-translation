import React from 'react';

const styles = {
  wrap: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 6,
    fontSize: 12,
    color: 'var(--accent)',
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: '50%',
    background: 'var(--accent)',
    animation: 'pulse 1s ease-in-out infinite',
  },
};

export function SpeakingIndicator({ isSpeaking }) {
  if (!isSpeaking) return null;
  return (
    <span style={styles.wrap}>
      <span style={styles.dot} />
      Speaking…
    </span>
  );
}
