import React from 'react';
import styles from './PilotageZone.module.scss';

export default function PilotageZone({ mode, value }) {
  return (
    <div className={styles.pilotageZone}>
      <span className={styles.label}>Pilotage</span>
      <div className={styles.content}>
        <div className={styles.mode}>{mode}</div>
        <div className={styles.value}>{value}</div>
        <div className={styles.spacer}></div>
      </div>
    </div>
  );
}
