import React from 'react';
import { DayStatus } from '../../models/HeatingCalendar';
import styles from './CalendarDay.module.scss';

export default function CalendarDay({
  day,
  isCurrentMonth,
  isSelected,
  onClick,
}) {
  const className = [
    styles.dayButton,
    !isCurrentMonth && styles.otherMonth,
    isSelected && styles.selected,
    day.status === DayStatus.DIFFERENT && styles.different,
    day.status === DayStatus.EMPTY && styles.empty,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <button
      className={className}
      onClick={onClick}
      disabled={day.status === DayStatus.EMPTY}
    >
      {day.date.day}
    </button>
  );
}
