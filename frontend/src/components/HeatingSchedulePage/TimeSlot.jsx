import React from 'react';
import styles from './TimeSlot.module.scss';

export default function TimeSlot({ left, width, value }) {
  const isOnOff = typeof value === 'string';
  const isTemperature = typeof value === 'number';

  const getSlotClass = () => {
    if (isOnOff) {
      return value === 'on' ? styles.on : styles.off;
    }

    if (isTemperature) {
      const temp = Math.round(value);

      if (temp < 16) return styles.tempCold;
      if (temp > 24) return styles.tempHot;

      // ex: temp20 → styles.temp20
      return styles[`temp${temp}`] || '';
    }

    return '';
  };

  const getLabel = () => {
    if (isOnOff) return value === 'on' ? 'ON' : 'OFF';
    if (isTemperature) return `${value}°`;
    return '';
  };

  const className = [styles.slot, getSlotClass()].filter(Boolean).join(' ');

  return (
    <div className={className} style={{ left, width }}>
      {getLabel()}
    </div>
  );
}
