import React from 'react';
import { HeatingMode } from '../../models/DailyHeatingPlan';
import styles from './TimeSlot.module.scss';

export default function TimeSlot({
  left, // Position en % (ex: "25%")
  width, // Largeur en % (ex: "10%")
  value, // Température (ex: 20) ou "on"/"off"
  mode, // "temp" ou "onoff"
}) {
  const getSlotClass = () => {
    if (mode === HeatingMode.ONOFF) {
      return value === 'on' ? styles.on : styles.off;
    }

    if (mode === HeatingMode.TEMPERATURE) {
      const temp = Math.round(value);

      if (temp < 16) return styles.tempCold;
      if (temp > 24) return styles.tempHot;

      return styles[`temp${temp}`];
    }

    return '';
  };

  const getLabel = () => {
    if (mode === HeatingMode.ONOFF) {
      return value === 'on' ? 'ON' : 'OFF';
    }
    return `${value}°`;
  };

  const className = [styles.slot, getSlotClass()].filter(Boolean).join(' ');

  return (
    <div className={className} style={{ left, width }}>
      {getLabel()}
    </div>
  );
}
