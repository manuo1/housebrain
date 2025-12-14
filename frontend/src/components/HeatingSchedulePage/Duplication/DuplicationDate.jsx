import React from 'react';
import styles from './DuplicationDate.module.scss';

export default function DuplicationDate({ label, value, onChange, min, max }) {
  return (
    <div className={styles.duplicationDate}>
      <label htmlFor={label}>{label}</label>
      <input
        type="date"
        id={label}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        min={min}
        max={max}
      />
    </div>
  );
}
