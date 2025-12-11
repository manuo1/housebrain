import React from 'react';
import styles from './WeekdaySelector.module.scss';

const WEEKDAYS = [
  { key: 'monday', label: 'L' },
  { key: 'tuesday', label: 'M' },
  { key: 'wednesday', label: 'M' },
  { key: 'thursday', label: 'J' },
  { key: 'friday', label: 'V' },
  { key: 'saturday', label: 'S' },
  { key: 'sunday', label: 'D' },
];

export default function WeekdaySelector({ selectedDays, onChange }) {
  const toggleDay = (day) => {
    if (selectedDays.includes(day)) {
      onChange(selectedDays.filter((d) => d !== day));
    } else {
      onChange([...selectedDays, day]);
    }
  };

  return (
    <div className={styles.weekdaySelector}>
      <label>Répéter les</label>
      <div className={styles.days}>
        {WEEKDAYS.map((day) => (
          <button
            key={day.key}
            className={selectedDays.includes(day.key) ? styles.active : ''}
            onClick={() => toggleDay(day.key)}
          >
            {day.label}
          </button>
        ))}
      </div>
    </div>
  );
}
