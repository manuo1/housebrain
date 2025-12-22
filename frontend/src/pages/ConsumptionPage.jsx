import React from 'react';
import ConsumptionBlock from '../components/ConsumptionBlock/ConsumptionBlock';
import styles from './ConsumptionPage.module.scss';

export default function DailyConsumptionPage() {
  return (
    <div className={styles.dailyConsumption}>
      <div className={styles.graphBlock}>
        <ConsumptionBlock />
      </div>
      <div className={styles.graphBlock}>
        <ConsumptionBlock />
      </div>
    </div>
  );
}
