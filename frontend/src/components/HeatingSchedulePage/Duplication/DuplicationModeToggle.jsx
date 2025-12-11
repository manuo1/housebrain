import React from 'react';
import styles from './DuplicationModeToggle.module.scss';

export default function DuplicationModeToggle({ mode, onChange }) {
  return (
    <div className={styles.modeToggle}>
      <button
        className={mode === 'day' ? styles.active : ''}
        onClick={() => onChange('day')}
      >
        Jours
      </button>
      <div className={styles.separator}></div>
      <button
        className={mode === 'week' ? styles.active : ''}
        onClick={() => onChange('week')}
      >
        Semaines
      </button>
    </div>
  );
}
