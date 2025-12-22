import React, { useState } from 'react';
import styles from './DateSelector.module.scss';

export default function DateSelector() {
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);

  const handlePrevious = () => {
    console.log('Previous day');
  };

  const handleNext = () => {
    console.log('Next day');
  };

  return (
    <div className={styles.dateSelector}>
      <button className={styles.navButton} onClick={handlePrevious}>
        ◄
      </button>

      <input
        type="date"
        className={styles.datePicker}
        value={date}
        onChange={(e) => setDate(e.target.value)}
      />

      <button className={styles.navButton} onClick={handleNext}>
        ►
      </button>
    </div>
  );
}
