import React from 'react';
import styles from './StepSelector.module.scss';
import { STEP_OPTIONS } from '../../../constants/consumptionConstants';

export default function StepSelector({ step, onChange }) {
  return (
    <div className={styles.stepSelector}>
      {STEP_OPTIONS.map(({ key, label }) => (
        <button
          key={key}
          type="button"
          className={`${styles.button} ${step === key ? styles.active : ''}`}
          onClick={() => onChange(key)}
        >
          {label}
        </button>
      ))}
    </div>
  );
}
