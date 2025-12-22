import React, { useState } from 'react';
import styles from './TimeStepSelector.module.scss';
import { STEP_OPTIONS } from '../../../constants/consumptionConstants';

export default function TimeStepSelector() {
  const [selected, setSelected] = useState(1);

  return (
    <div className={styles.timeStepSelector}>
      {STEP_OPTIONS.map(({ key, label }) => (
        <button
          key={key}
          className={`${styles.button} ${
            selected === key ? styles.active : ''
          }`}
          onClick={() => setSelected(key)}
        >
          {label}
        </button>
      ))}
    </div>
  );
}
