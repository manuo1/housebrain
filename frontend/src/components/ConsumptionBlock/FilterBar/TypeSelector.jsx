import React, { useState } from 'react';
import styles from './TypeSelector.module.scss';
import { VALUE_TYPES } from '../../../constants/consumptionConstants';

export default function TypeSelector() {
  const [selected, setSelected] = useState('wh');

  return (
    <div className={styles.typeSelector}>
      {VALUE_TYPES.map(({ key, label }) => (
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
