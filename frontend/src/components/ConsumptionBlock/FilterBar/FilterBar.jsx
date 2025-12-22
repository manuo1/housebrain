import React from 'react';
import TypeSelector from './TypeSelector';
import TimeStepSelector from './TimeStepSelector';
import DateSelector from './DateSelector';
import styles from './FilterBar.module.scss';

export default function FilterBar() {
  return (
    <div className={styles.filterBar}>
      <TypeSelector />
      <DateSelector />
      <TimeStepSelector />
    </div>
  );
}
