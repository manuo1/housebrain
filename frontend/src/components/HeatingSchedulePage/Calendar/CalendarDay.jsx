import React from 'react';
import { DayStatus } from '../../../models/HeatingCalendar';
import styles from './CalendarDay.module.scss';

export default function CalendarDay({
  day,
  isCurrentMonth,
  isSelected,
  isToday,
  onClick,
}) {
  const className = [
    styles.dayButton,
    !isCurrentMonth && styles.otherMonth,
    isSelected && styles.selected,
    isToday && styles.today,
    day.status === DayStatus.DIFFERENT && styles.different,
    day.status === DayStatus.EMPTY && styles.empty,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <button className={className} onClick={onClick}>
      {day.date.day}
    </button>
  );
}
