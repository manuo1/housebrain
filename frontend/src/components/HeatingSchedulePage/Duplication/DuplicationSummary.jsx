import React from 'react';
import styles from './DuplicationSummary.module.scss';

const WEEKDAY_LABELS = {
  monday: 'lundis',
  tuesday: 'mardis',
  wednesday: 'mercredis',
  thursday: 'jeudis',
  friday: 'vendredis',
  saturday: 'samedis',
  sunday: 'dimanches',
};

export default function DuplicationSummary({
  mode,
  sourceDate,
  endDate,
  selectedRooms,
  selectedWeekdays,
}) {
  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const [year, month, day] = dateStr.split('-');
    return `${day}/${month}/${year}`;
  };

  const getWeekdaysList = () => {
    return selectedWeekdays.map((day) => WEEKDAY_LABELS[day]).join(', ');
  };

  return (
    <div className={styles.summary}>
      <label>Récapitulatif :</label>
      <div className={styles.content}>
        <div className={styles.section}>
          Le planning du {formatDate(sourceDate)}
          {mode === 'week' && ' (semaine complète)'} des pièces :
        </div>

        <div className={styles.list}>
          {selectedRooms.map((room) => (
            <div key={room.id} className={styles.item}>
              • {room.name}
            </div>
          ))}
        </div>

        {mode === 'day' && selectedWeekdays.length > 0 && (
          <>
            <div className={styles.section}>Sera dupliqué tous les :</div>
            <div className={styles.list}>
              <div className={styles.item}>• {getWeekdaysList()}</div>
            </div>
          </>
        )}

        {mode === 'week' && (
          <>
            <div className={styles.section}>Sera dupliqué chaque semaine</div>
          </>
        )}

        <div className={styles.section}>Jusqu'au :</div>
        <div className={styles.list}>
          <div className={styles.highlight}>• {formatDate(endDate)}</div>
        </div>
      </div>
    </div>
  );
}
