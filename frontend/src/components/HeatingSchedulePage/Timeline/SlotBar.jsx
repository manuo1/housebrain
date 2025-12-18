import React from 'react';
import TimeSlot from './TimeSlot';
import { calculateSlotPosition, percentToTime } from './utils/slotCalculations';
import styles from './SlotBar.module.scss';

export default function SlotBar({ slots, onSlotClick, onEmptyClick }) {
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

      const clickTime = percentToTime(percentClick);
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
