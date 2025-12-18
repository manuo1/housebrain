import React from 'react';
import { getSlotClass, getLabel } from './utils/slotTypes';
import styles from './TimeSlot.module.scss';

export default function TimeSlot({ left, width, value, start, end, onClick }) {
  const className = [styles.slot, getSlotClass(value, styles)]
    .filter(Boolean)
    .join(' ');

  const handleClick = () => {
    if (onClick) {
      onClick({ start, end, value });
    }
  };

  return (
    <div
      className={className}
      style={{ left, width }}
      title={`${start} - ${end}`}
      onClick={handleClick}
    >
      {getLabel(value)}
    </div>
  );
}
