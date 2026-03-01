import { useState, useEffect, useMemo } from "react";
import FilterBar from "./FilterBar/FilterBar";
import TotalsCards from "./TotalsCards/TotalsCards";
import styles from "./ConsumptionBlock.module.scss";
import StepChart from "./StepChart/StepChart";
import fetchDailyConsumption from "../../services/fetchDailyConsumption";
import transformDailyConsumptionToChart from "../../transformers/consumptionToChart/consumptionToChart";
import { DisplayType } from "../../transformers/consumptionToChart/computeAxisY";
import { ChartPoint } from "../../transformers/consumptionToChart/computeChartValues";
import DailyIndexes from "../../models/DailyConsumption";

export interface ChartData {
  axisY: { labels: string[] };
  axisX: { labels: string[] };
  values: ChartPoint[];
}

export default function ConsumptionBlock() {
  const [date, setDate] = useState<string>(new Date().toISOString().split("T")[0]);
  const [step, setStep] = useState<number>(1);
  const [displayType, setDisplayType] = useState<DisplayType>("wh");
  const [dailyConsumption, setDailyConsumption] = useState<DailyIndexes | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      setError(null);
      setDailyConsumption(null);

      try {
        const data = await fetchDailyConsumption(date, step);
        setDailyConsumption(data);
      } catch (err) {
        console.error("Error loading consumption data:", err);
        setError((err as Error).message);
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, [date, step]);

  const chartData = useMemo((): ChartData | null => {
    if (error || !dailyConsumption) return null;
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
