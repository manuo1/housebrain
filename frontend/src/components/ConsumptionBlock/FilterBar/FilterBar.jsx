import React from 'react';
import TypeSelector from './TypeSelector';
import TimeStepSelector from './TimeStepSelector';
import DateSelector from './DateSelector';
import styles from './FilterBar.module.scss';

export default function FilterBar({ displayType, onDisplayTypeChange }) {
  return (
    <div className={styles.filterBar}>
      <TypeSelector value={displayType} onChange={onDisplayTypeChange} />
      <DateSelector />
      <TimeStepSelector />
    </div>
  );
}
