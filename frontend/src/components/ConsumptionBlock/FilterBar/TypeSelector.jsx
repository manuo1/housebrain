import React from 'react';
import styles from './TypeSelector.module.scss';
import { VALUE_TYPES } from '../../../constants/consumptionConstants';

export default function TypeSelector({ value, onChange }) {
  return (
    <div className={styles.typeSelector}>
      {VALUE_TYPES.map(({ key, label }) => (
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
