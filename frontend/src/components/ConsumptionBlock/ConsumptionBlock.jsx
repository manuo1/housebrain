import React from 'react';
import FilterBar from './FilterBar/FilterBar';
import TotalsCards from './TotalsCards/TotalsCards';
import styles from './ConsumptionBlock.module.scss';
import StepChart from './StepChart/StepChart';
import { mockConsumption } from '../../mocks/mockConsumption';

export default function ConsumptionBlock() {
  return (
    <div className={styles.consumptionBlock}>
      <FilterBar />
      <StepChart data={mockConsumption} />
      <TotalsCards />
    </div>
  );
}
