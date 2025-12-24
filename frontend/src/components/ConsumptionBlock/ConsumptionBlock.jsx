import React, { useState, useEffect, useMemo } from 'react';
import FilterBar from './FilterBar/FilterBar';
import TotalsCards from './TotalsCards/TotalsCards';
import styles from './ConsumptionBlock.module.scss';
import StepChart from './StepChart/StepChart';
import fetchDailyConsumption from '../../services/fetchDailyConsumption';
import transformDailyConsumptionToChart from '../../transformers/consumptionToChart/consumptionToChart';

export default function ConsumptionBlock() {
  // States
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const [step, setStep] = useState(1);
  const [displayType, setDisplayType] = useState('wh');
  const [dailyConsumption, setDailyConsumption] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch data quand date ou step changent
  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const data = await fetchDailyConsumption(date, step);
        setDailyConsumption(data);
      } catch (err) {
        console.error('Error loading consumption data:', err);
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, [date, step]);

  // Transform data pour le chart
  const chartData = useMemo(() => {
    if (!dailyConsumption) return null;
    return transformDailyConsumptionToChart(dailyConsumption, displayType);
  }, [dailyConsumption, displayType]);

  return (
    <div className={styles.consumptionBlock}>
      <FilterBar
        displayType={displayType}
        onDisplayTypeChange={setDisplayType}
        step={step}
        onStepChange={setStep}
        date={date}
        onDateChange={setDate}
      />

      {isLoading && <div>Chargement...</div>}
      {error && <div>Erreur : {error}</div>}
      {chartData && <StepChart data={chartData} />}

      <TotalsCards />
    </div>
  );
}
