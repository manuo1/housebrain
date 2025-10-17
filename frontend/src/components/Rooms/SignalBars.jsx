import React from 'react';
import styles from './SignalBars.module.scss';

export default function SignalBars({ strength }) {
  return (
    <div className={styles.signalBars}>
      {[1, 2, 3, 4, 5].map((bar) => (
        <div
          key={bar}
          className={`${styles.bar} ${bar <= strength ? styles.active : ''}`}
        />
      ))}
    </div>
  );
}
