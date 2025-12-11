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

// -----------------------------------------------------------
// Utils
// -----------------------------------------------------------
function formatDate(dateStr) {
  if (!dateStr) return '';
  const [year, month, day] = dateStr.split('-');
  return `${day}/${month}/${year}`;
}

function getWeekRange(dateStr) {
  const date = new Date(dateStr);
  const day = date.getDay(); // 0 = sunday ... 6 = saturday
  const jsDay = day === 0 ? 7 : day; // convert 0→7 pour dimanche

  const monday = new Date(date);
  monday.setDate(date.getDate() - (jsDay - 1));

  const sunday = new Date(date);
  sunday.setDate(date.getDate() + (7 - jsDay));

  const format = (d) =>
    String(d.getDate()).padStart(2, '0') +
    '/' +
    String(d.getMonth() + 1).padStart(2, '0') +
    '/' +
    d.getFullYear();

  return {
    monday: monday.toISOString().slice(0, 10),
    sunday: sunday.toISOString().slice(0, 10),
    mondayText: format(monday),
    sundayText: format(sunday),
  };
}

// -----------------------------------------------------------
// Component
// -----------------------------------------------------------
export default function DuplicationSummary({
  mode,
  sourceDate,
  endDate,
  selectedRooms,
  selectedWeekdays,
}) {
  const startWeekRange = mode === 'week' ? getWeekRange(sourceDate) : null;
  const endWeekRange =
    mode === 'week' && endDate ? getWeekRange(endDate) : null;
  const getWeekdaysList = () => {
    return selectedWeekdays.map((day) => WEEKDAY_LABELS[day]).join(', ');
  };

  return (
    <div className={styles.summary}>
      <div className={styles.content}>
        {/* TITRE + DATE(S) */}
        <div className={styles.section}>
          {mode !== 'week' ? (
            <>
              Le planning du :<br />
              {formatDate(sourceDate)}
              <br />
              des pièces :
            </>
          ) : (
            <>
              Les planning de la semaine du :<br />
              {startWeekRange.mondayText} au {startWeekRange.sundayText}
              <br />
              des pièces :
            </>
          )}
        </div>

        {/* LISTE DES PIÈCES */}
        <div className={styles.list}>
          {selectedRooms.map((room) => (
            <div key={room.id} className={styles.item}>
              • {room.name}
            </div>
          ))}
        </div>

        {/* MODE DAY : WEEKDAYS */}
        {mode === 'day' && selectedWeekdays.length > 0 && (
          <>
            <div className={styles.section}>Sera dupliqué tous les :</div>
            <div className={styles.list}>
              <div className={styles.item}>• {getWeekdaysList()}</div>
            </div>
          </>
        )}

        {/* MODE WEEK */}
        {mode === 'week' && endDate && (
          <div className={styles.section}>Seront dupliqués chaque semaine</div>
        )}

        {/* END DATE */}
        {endDate && (
          <div className={styles.section}>
            {mode === 'week' ? (
              <>
                Jusqu'à la semaine du :<br />
                {endWeekRange?.mondayText} au {endWeekRange?.sundayText}
              </>
            ) : (
              <>
                Jusqu'au :<br />
                {formatDate(endDate)}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
