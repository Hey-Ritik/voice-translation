import React from 'react';

const styles = {
  button: {
    width: 80,
    height: 80,
    borderRadius: '50%',
    border: 'none',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: 'pointer',
    transition: 'transform 0.15s ease, box-shadow 0.15s ease',
    background: 'var(--accent)',
    color: '#0f0f12',
  },
  buttonStop: {
    background: 'var(--danger)',
    color: '#fff',
  },
  buttonDisabled: {
    opacity: 0.5,
    cursor: 'not-allowed',
  },
  svg: {
    width: 32,
    height: 32,
  },
};

export function MicButton({ isRecording, onStart, onStop, disabled }) {
  const handleClick = () => {
    if (disabled) return;
    if (isRecording) onStop?.();
    else onStart?.();
  };

  return (
    <button
      type="button"
      aria-label={isRecording ? 'Stop recording' : 'Start recording'}
      style={{
        ...styles.button,
        ...(isRecording ? styles.buttonStop : {}),
        ...(disabled ? styles.buttonDisabled : {}),
      }}
      onMouseDown={(e) => e.preventDefault()}
      onClick={handleClick}
      disabled={disabled}
    >
      {isRecording ? (
        <svg style={styles.svg} viewBox="0 0 24 24" fill="currentColor">
          <rect x="6" y="6" width="12" height="12" rx="2" />
        </svg>
      ) : (
        <svg style={styles.svg} viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
          <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
        </svg>
      )}
    </button>
  );
}
