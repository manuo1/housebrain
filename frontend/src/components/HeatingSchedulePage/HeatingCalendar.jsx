// frontend/src/components/HeatingSchedulePage/HeatingCalendar.jsx

import React from 'react';
import { getMonthLabel } from '../../utils/dateUtils';
import CalendarDay from './CalendarDay';
import styles from './HeatingCalendar.module.scss';

export default function HeatingCalendar({
  calendar,
  selectedDate,
  onDateSelect,
  onMonthChange,
}) {
  if (!calendar) {
    return <div className={styles.loading}>Chargement du calendrier...</div>;
  }

  const handlePrevMonth = () => {
    const newMonth = calendar.month === 1 ? 12 : calendar.month - 1;
    const newYear = calendar.month === 1 ? calendar.year - 1 : calendar.year;
    onMonthChange(newYear, newMonth);
  };

  const handleNextMonth = () => {
    const newMonth = calendar.month === 12 ? 1 : calendar.month + 1;
    const newYear = calendar.month === 12 ? calendar.year + 1 : calendar.year;
    onMonthChange(newYear, newMonth);
  };

  // Group days by weeks (7 days per week)
  const weeks = [];
  for (let i = 0; i < calendar.days.length; i += 7) {
    weeks.push(calendar.days.slice(i, i + 7));
  }

  const monthLabel = `${getMonthLabel(calendar.month)} ${calendar.year}`;
  const selectedDateISO = selectedDate;

  return (
    <div className={styles.calendar}>
      <div className={styles.header}>
        <button
          className={styles.navBtn}
          onClick={handlePrevMonth}
          aria-label="Mois précédent"
        >
          ◀
        </button>
        <h4 className={styles.title}>{monthLabel}</h4>
        <button
          className={styles.navBtn}
          onClick={handleNextMonth}
          aria-label="Mois suivant"
        >
          ▶
        </button>
      </div>

      <table className={styles.calendarTable}>
        <thead>
          <tr>
            <th>L</th>
            <th>M</th>
            <th>M</th>
            <th>J</th>
            <th>V</th>
            <th>S</th>
            <th>D</th>
          </tr>
        </thead>
        <tbody>
          {weeks.map((week, weekIndex) => (
            <tr key={weekIndex}>
              {week.map((day) => {
                const dateISO = day.date.toISO();
                const isCurrentMonth = day.date.month === calendar.month;
                const isSelected = dateISO === selectedDateISO;

                return (
                  <td key={dateISO}>
                    <CalendarDay
                      day={day}
                      isCurrentMonth={isCurrentMonth}
                      isSelected={isSelected}
                      onClick={() => onDateSelect(dateISO)}
                    />
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
