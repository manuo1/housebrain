import React from 'react';
import styles from './TimeStepSelector.module.scss';
import { STEP_OPTIONS } from '../../../constants/consumptionConstants';

export default function TimeStepSelector({ value, onChange }) {
  return (
    <div className={styles.timeStepSelector}>
      {STEP_OPTIONS.map(({ key, label }) => (
        <button
          key={key}
          className={`${styles.button} ${value === key ? styles.active : ''}`}
          onClick={() => onChange(key)}
        >
          {label}
        </button>
      ))}
    </div>
  );
}
