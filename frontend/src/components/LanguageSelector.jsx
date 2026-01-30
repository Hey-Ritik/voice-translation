import React, { useEffect, useState } from 'react';

const API_BASE = import.meta.env.VITE_API_URL ?? '';

const styles = {
  wrap: {
    display: 'flex',
    flexDirection: 'column',
    gap: 6,
  },
  label: {
    fontSize: 12,
    fontWeight: 600,
    color: 'var(--text-muted)',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
  },
  select: {
    padding: '10px 14px',
    borderRadius: 'var(--radius)',
    border: '1px solid var(--border)',
    background: 'var(--surface)',
    color: 'var(--text)',
    fontSize: 15,
    fontFamily: 'inherit',
    minWidth: 200,
    cursor: 'pointer',
  },
};

export function LanguageSelector({ value, onChange, disabled }) {
  const [languages, setLanguages] = useState([
    { code: 'hi', name: 'Hindi' },
    { code: 'en', name: 'English' },
    { code: 'bn', name: 'Bengali' },
    { code: 'ta', name: 'Tamil' },
    { code: 'te', name: 'Telugu' },
    { code: 'mr', name: 'Marathi' },
    { code: 'ur', name: 'Urdu' },
    { code: 'pa', name: 'Punjabi' },
    { code: 'gu', name: 'Gujarati' },
    { code: 'kn', name: 'Kannada' },
    { code: 'ml', name: 'Malayalam' },
  ]);

  useEffect(() => {
    const url = API_BASE ? `${API_BASE.replace(/\/$/, '')}/languages` : '/languages';
    fetch(url)
      .then((r) => r.ok ? r.json() : null)
      .then((data) => {
        if (data?.languages?.length) setLanguages(data.languages);
      })
      .catch(() => {});
  }, []);

  return (
    <div style={styles.wrap}>
      <label style={styles.label} htmlFor="target-lang">
        Target language
      </label>
      <select
        id="target-lang"
        style={styles.select}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
      >
        {languages.map(({ code, name }) => (
          <option key={code} value={code}>
            {name}
          </option>
        ))}
      </select>
    </div>
  );
}
