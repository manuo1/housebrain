import React, { useMemo } from 'react';
import FilterBar from './FilterBar/FilterBar';
import TotalsCards from './TotalsCards/TotalsCards';
import styles from './ConsumptionBlock.module.scss';
import StepChart from './StepChart/StepChart';
import { mockDailyConsumption60 } from '../../mocks/mockDailyConsumption60';
import transformDailyConsumptionToChart from '../../transformers/consumptionToChart/consumptionToChart';

export default function ConsumptionBlock() {
  // Pour l'instant en dur, plus tard ce sera dynamique via TypeSelector
  const displayType = 'wh';

  const chartData = useMemo(
    () => transformDailyConsumptionToChart(mockDailyConsumption60, displayType),
    [displayType]
  );

  console.log('Chart data transformed:', chartData); // Debug

  return (
    <div className={styles.consumptionBlock}>
      <FilterBar />
      <StepChart data={chartData} />
      <TotalsCards />
    </div>
  );
}
