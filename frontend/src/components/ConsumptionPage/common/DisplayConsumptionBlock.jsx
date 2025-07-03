import React, { useState, useEffect } from "react";
import DatePicker from "../../common/DatePicker";
import PeriodPicker from "../../common/PeriodPicker"; // à créer
import ValueSelector from "../common/ValueSelector";
import StepSelector from "../common/StepSelector";
import TotalsDisplay from "../common/TotalsDisplay";
import DailyConsumptionChart from "../DailyConsumptionChart/DailyConsumptionChart";
import PeriodConsumptionChart from "../PeriodConsumptionChart/PeriodConsumptionChart"; // à créer
import Loader from "../../common/Loader";
import fetchDailyConsumption from "../../../services/fetchDailyConsumption";
import fetchConsumptionByPeriod from "../../../services/fetchfetchPeriodConsumption";
import styles from "./DisplayConsumptionBlock.module.scss";

export default function DisplayConsumptionBlock() {
  const today = new Date().toISOString().slice(0, 10);

  const [date, setDate] = useState(today);
  const [endDate, setEndDate] = useState(today);
  const [step, setStep] = useState(1);
  const [valueType, setValueType] = useState("average_watt");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const isDailyStep = [1, 30, 60].includes(step);

  useEffect(() => {
    const isDailyStep = [1, 30, 60].includes(step);
    const loadData = async () => {
      setLoading(true);
      setError(null);
      try {
        const result = isDailyStep
          ? await fetchDailyConsumption(date, step) // step = 1|30|60
          : await fetchConsumptionByPeriod(date, endDate, step); // step = day|week|month
        setData(result);
      } catch (err) {
        setError(err.message || "Unknown error");
        setData(null);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [date, endDate, step]);

  function renderChart() {
    if (!data) return null;

    if (isDailyStep) {
      return (
        <DailyConsumptionChart
          data={data.data}
          chartType={valueType === "average_watt" ? "line" : "area"}
          valueKey={valueType}
        />
      );
    } else {
      return <PeriodConsumptionChart data={data.data} valueType={valueType} />;
    }
  }

  return (
    <div className={styles.block}>
      <div className={styles.selectors}>
        <ValueSelector value={valueType} onChange={setValueType} />
        {isDailyStep ? (
          <DatePicker value={date} onChange={setDate} />
        ) : (
          <PeriodPicker
            startDate={date}
            endDate={endDate}
            onStartChange={setDate}
            onEndChange={setEndDate}
          />
        )}
        <StepSelector step={step} onChange={setStep} />
      </div>
      <div className={styles.data}>
        {data && renderChart()}
        {data && <TotalsDisplay totals={data.totals} />}
        {loading && (
          <div className={styles.loaderOverlay}>
            <Loader />
          </div>
        )}
        {error && <p className={styles.error}>Error: {error}</p>}
      </div>
    </div>
  );
}
