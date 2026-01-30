import React from 'react';

const styles = {
  footer: {
    padding: '24px 16px',
    textAlign: 'center',
    color: 'var(--text-muted)',
    fontSize: '0.875rem',
    marginTop: 'auto',
    fontFamily: 'var(--font-sans)',
    borderTop: '1px solid var(--border)',
    background: 'var(--bg)', // Ensure it blends with the background
  },
  link: {
    color: 'var(--text-muted)',
    textDecoration: 'none',
    opacity: 0.8,
    transition: 'opacity 0.2s',
  },
  container: {
    maxWidth: 800,
    margin: '0 auto',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    gap: '8px',
  }
};

export const Footer = () => {
  return (
    <footer style={styles.footer}>
      <div style={styles.container}>
        <span>Built in collaboration between <strong>Broadrange.AI</strong> and <strong>RV University, Bangalore</strong></span>
      </div>
    </footer >
  );
};
