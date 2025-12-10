import React from 'react';
import TimeSlot from './TimeSlot';
import styles from './SlotBar.module.scss';

export default function SlotBar({ slots, onSlotClick, onEmptyClick }) {
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

  const handleSlotClick = (slotData, index) => {
    if (onSlotClick) {
      onSlotClick(slotData, index);
    }
  };

  const handleBarClick = (e) => {
    // Check if click was on the bar itself, not on a slot
    if (e.target.className.includes('slotBar') && onEmptyClick) {
      const rect = e.currentTarget.getBoundingClientRect();
      const clickX = e.clientX - rect.left;
      const percentClick = (clickX / rect.width) * 100;

      // Convert percent to time
      const totalMinutes = Math.round((percentClick / 100) * 1440);
      const hours = Math.floor(totalMinutes / 60);
      const minutes = totalMinutes % 60;
      const clickTime = `${String(hours).padStart(2, '0')}:${String(
        minutes
      ).padStart(2, '0')}`;

      onEmptyClick(clickTime);
    }
  };

  return (
    <div className={styles.slotBar} onClick={handleBarClick}>
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
            onClick={(slotData) => handleSlotClick(slotData, index)}
          />
        );
      })}
    </div>
  );
}
