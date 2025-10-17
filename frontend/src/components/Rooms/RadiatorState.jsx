import React from 'react';
import styles from './RadiatorState.module.scss';

const getStateInfo = (state) => {
  switch (state) {
    case null:
      return { label: 'Pas de radiateur', className: 'undefined' };
    case 'on':
      return { label: 'Allumé', className: 'on' };
    case 'off':
      return { label: 'Éteint', className: 'off' };
    case 'turning_on':
      return { label: 'Allumage', className: 'turning' };
    case 'shutting_down':
      return { label: 'Arrêt', className: 'turning' };
    case 'load_shed':
      return { label: 'Délestage', className: 'loadShed' };
    default:
      return { label: 'Indéfini', className: 'undefined' };
  }
};

export default function RadiatorState({ radiatorState }) {
  const stateInfo = getStateInfo(radiatorState);

  return (
    <div className={`${styles.radiatorState} ${styles[stateInfo.className]}`}>
      <span className={styles.label}>{stateInfo.label}</span>
    </div>
  );
}
