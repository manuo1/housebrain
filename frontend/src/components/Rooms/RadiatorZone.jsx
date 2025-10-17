import React from 'react';
import styles from './RadiatorZone.module.scss';

export default function RadiatorZone({ state }) {
  const getStateInfo = (state) => {
    switch (state) {
      case null:
        return { label: 'Pas de radiateur', className: 'undefined' };
      case 'on':
        return { label: 'Allumé', className: 'on' };
      case 'off':
        return { label: 'Éteint', className: 'off' };
      case 'turning_on':
        return { label: 'Allumage', className: 'turning_on' };
      case 'shutting_down':
        return { label: 'Arrêt', className: 'shutting_down' };
      case 'load_shed':
        return { label: 'Délestage', className: 'load_shed' };
      default:
        return { label: 'Indéfini', className: 'undefined' };
    }
  };

  const stateInfo = getStateInfo(state);

  return (
    <div className={styles.radiatorZone}>
      <span className={styles.label}>Radiateur</span>
      <div className={`${styles.content} ${styles[stateInfo.className]}`}>
        <span className={styles.stateLabel}>{stateInfo.label}</span>
      </div>
    </div>
  );
}
