import React from 'react';
import styles from './DuplicationEndDate.module.scss';

export default function DuplicationEndDate({ value, onChange }) {
  return (
    <div className={styles.endDate}>
      <label htmlFor="endDate">Date de fin</label>
      <input
        type="date"
        id="endDate"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
}
