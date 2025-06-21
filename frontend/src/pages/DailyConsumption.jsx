import React, { useState, useEffect } from "react";
import DatePicker from "../components/DatePicker";
import ValueSelector from "../components/ValueSelector";
import StepSelector from "../components/StepSelector";
import TotalsDisplay from "../components/TotalsDisplay";
import DailyConsumptionChart from "../components/DailyConsumptionChart";
import Loader from "../components/Loader";
import fetchDailyIndexes from "../services/fetchDailyIndexes";
import styles from "./DailyConsumption.module.scss";

export default function DailyConsumption() {
  const today = new Date().toISOString().slice(0, 10);

  const [date, setDate] = useState(today);
  const [step, setStep] = useState(1); // valeurs autorisées : 1, 30, 60
  const [valueType, setValueType] = useState("average_watt"); // "wh", "average_watt", "euros"
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  function renderChart() {
    if (!data) return null;

    switch (valueType) {
      case "average_watt":
        return (
          <DailyConsumptionChart
            data={data.data}
            chartType="line"
            valueKey="average_watt"
          />
        );
      case "wh":
        return (
          <DailyConsumptionChart
            data={data.data}
            chartType="area"
            valueKey="wh"
          />
        );
      case "euros":
        return (
          <DailyConsumptionChart
            data={data.data}
            chartType="area"
            valueKey="euros"
          />
        );
      default:
        return null;
    }
  }

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      setError(null);
      try {
        const result = await fetchDailyIndexes(date, step);
        setData(result);
      } catch (err) {
        setError(err.message || "Unknown error");
        setData(null);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [date, step]);

  return (
    <div className={styles.dailyConsumption}>
      <div className={styles.selectors}>
        <ValueSelector value={valueType} onChange={setValueType} />
        <DatePicker value={date} onChange={setDate} />
        <StepSelector step={step} onChange={setStep} />
      </div>
      <div className={styles.data}>
        {data && renderChart()}
        {data && <TotalsDisplay totals={data.totals} />}
      </div>
      {loading && <Loader />}
      {error && <p className={styles.error}>Error: {error}</p>}
    </div>
  );
}
