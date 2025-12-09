import React from 'react';
import styles from './TimeSlot.module.scss';

export default function TimeSlot({ left, width, value }) {
  const lower = value.toLowerCase();
  const isOnOff = lower === 'on' || lower === 'off';

  const tempValue = Number(value);
  const isTemperature = !isNaN(tempValue);

  const getSlotClass = () => {
    if (isOnOff) {
      return lower === 'on' ? styles.on : styles.off;
    }

    if (isTemperature) {
      const temp = Math.round(tempValue);

      if (temp < 16) return styles.tempCold;
      if (temp > 24) return styles.tempHot;

      return styles[`temp${temp}`] || '';
    }

    return '';
  };

  const getLabel = () => {
    if (isOnOff) return lower === 'on' ? 'ON' : 'OFF';
    if (isTemperature) return `${tempValue}°`;
    return value;
  };

  const className = [styles.slot, getSlotClass()].filter(Boolean).join(' ');

  return (
    <div className={className} style={{ left, width }}>
      {getLabel()}
    </div>
  );
}
