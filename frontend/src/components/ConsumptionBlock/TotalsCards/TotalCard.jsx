import React from 'react';
import styles from './TotalCard.module.scss';

export default function TotalCard({ label, kwh, euros }) {
  return (
    <div className={styles.card}>
      <div className={styles.label}>{label} : </div>
      <div className={styles.kwh}>{kwh}</div>
      <div className={styles.separator}>/</div>
      <div className={styles.euros}>{euros}</div>
    </div>
  );
}
