import React from 'react';
import styles from './HeatingControl.module.scss';

const MODE_LABELS = {
  thermostat: 'Thermostat',
  on_off: 'On/Off',
};

const VALUE_LABELS = {
  on: 'On',
  off: 'Off',
  unknown: 'Inconnu',
};

export default function HeatingControl({ heatingModeValue, heatingModeLabel }) {
  if (heatingModeValue === null && heatingModeLabel === null) {
    return <div className={styles.heatingModeValue}>-</div>;
  }

  const displayLabel = MODE_LABELS[heatingModeLabel] || heatingModeLabel;
  const displayValue = VALUE_LABELS[heatingModeValue] || `${heatingModeValue}°`;

  return (
    <div className={styles.heatingModeValue}>
      {displayLabel} : {displayValue}
    </div>
  );
}
