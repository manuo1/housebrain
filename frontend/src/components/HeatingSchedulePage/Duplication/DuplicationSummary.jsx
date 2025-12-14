import React from 'react';
import { formatDate, getWeekRange } from './duplicationDateUtils';
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
  startDate,
  endDate,
  selectedRooms,
  selectedWeekdays,
}) {
  const sourceWeekRange = mode === 'week' ? getWeekRange(sourceDate) : null;
  const startWeekRange =
    mode === 'week' && startDate ? getWeekRange(startDate) : null;
  const endWeekRange =
    mode === 'week' && endDate ? getWeekRange(endDate) : null;

  const getWeekdaysList = () => {
    return selectedWeekdays.map((day) => WEEKDAY_LABELS[day]).join(', ');
  };

  return (
    <div className={styles.summary}>
      <div className={styles.content}>
        {/* TITRE + DATE(S) SOURCE */}
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
              {sourceWeekRange?.mondayText} au {sourceWeekRange?.sundayText}
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
        {mode === 'week' && (
          <div className={styles.section}>Seront dupliqués chaque semaine</div>
        )}

        {/* START DATE */}
        {startDate && (
          <div className={styles.section}>
            {mode === 'week' ? (
              <>
                Depuis la semaine du :<br />
                {startWeekRange?.mondayText} au {startWeekRange?.sundayText}
              </>
            ) : (
              <>
                Depuis le :<br />
                {formatDate(startDate)}
              </>
            )}
          </div>
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
