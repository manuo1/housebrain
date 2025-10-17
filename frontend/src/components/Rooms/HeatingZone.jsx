import React from 'react';
import RadiatorState from './RadiatorState';
import HeatingControl from './HeatingControl';
import styles from './HeatingZone.module.scss';

export default function HeatingZone({
  heatingModeLabel,
  heatingModeValue,
  radiatorState,
}) {
  return (
    <fieldset className={styles.heatingZone}>
      <legend className={styles.label}>Chauffage</legend>
      <RadiatorState radiatorState={radiatorState} />
      <HeatingControl
        heatingModeValue={heatingModeValue}
        heatingModeLabel={heatingModeLabel}
      />
    </fieldset>
  );
}
