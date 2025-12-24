import React from 'react';
import styles from './DateSelector.module.scss';
import { addDays } from '../../../utils/dateUtils';

export default function DateSelector({ value, onChange }) {
  const handlePrevious = () => {
    onChange(addDays(value, -1));
  };

  const handleNext = () => {
    const today = new Date().toISOString().split('T')[0];
    if (value < today) {
      onChange(addDays(value, 1));
    }
  };

  return (
    <div className={styles.dateSelector}>
      <button className={styles.navButton} onClick={handlePrevious}>
        ◄
      </button>
      <input
        type="date"
        className={styles.datePicker}
        value={value}
        max={new Date().toISOString().split('T')[0]}
        onChange={(e) => onChange(e.target.value)}
      />
      <button className={styles.navButton} onClick={handleNext}>
        ►
      </button>
    </div>
  );
}
