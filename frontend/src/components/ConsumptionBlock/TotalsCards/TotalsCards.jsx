import React from 'react';
import TotalCard from './TotalCard';
import styles from './TotalsCards.module.scss';

export default function TotalsCards() {
  return (
    <div className={styles.totalsCards}>
      <TotalCard label="Heures Creuses" kwh="123.45" euros="4.59" />
      <TotalCard label="Heures Pleines" kwh="123.45" euros="4.59" />
      <TotalCard label="Total" kwh="123.45" euros="4.59" />
    </div>
  );
}
