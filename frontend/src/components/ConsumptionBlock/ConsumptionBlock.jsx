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
      setDailyConsumption(null);

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
    if (error || !dailyConsumption) return null; // null si erreur OU pas de données
    return transformDailyConsumptionToChart(dailyConsumption, displayType);
  }, [dailyConsumption, displayType, error]);

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

      <StepChart data={chartData} />

      <TotalsCards totals={dailyConsumption?.totals} />

      {(isLoading || error) && (
        <div className={styles.overlay}>
          {isLoading && <div className={styles.spinner}></div>}
          {error && (
            <div className={styles.error}>
              <div className={styles.errorIcon}>⚠️</div>
              <div className={styles.errorMessage}>Un problème est survenu</div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
