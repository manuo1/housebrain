import React from 'react';
import TimeSlot from './TimeSlot';
import styles from './SlotBar.module.scss';

export default function SlotBar({ slots }) {
  // Fonction pour convertir HH:MM en pourcentage de la journée
  const timeToPercent = (timeStr) => {
    const [hours, minutes] = timeStr.split(':').map(Number);
    const totalMinutes = hours * 60 + minutes;
    return (totalMinutes / 1440) * 100; // 1440 = 24h * 60min
  };

  // Calcul de la position et largeur de chaque slot
  const calculateSlotPosition = (slot) => {
    const startPercent = timeToPercent(slot.start);
    const endPercent = timeToPercent(slot.end);
    const widthPercent = endPercent - startPercent;

    return {
      left: `${startPercent}%`,
      width: `${widthPercent}%`,
    };
  };

  return (
    <div className={styles.slotBar}>
      {slots.map((slot, index) => {
        const { left, width } = calculateSlotPosition(slot);

        return (
          <TimeSlot
            key={index}
            left={left}
            width={width}
            value={slot.value}
            start={slot.start}
            end={slot.end}
          />
        );
      })}
    </div>
  );
}
