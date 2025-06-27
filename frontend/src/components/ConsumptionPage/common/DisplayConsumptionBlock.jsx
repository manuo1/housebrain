import React, { useState, useEffect } from "react";
import DatePicker from "../../common/DatePicker";
import ValueSelector from "../common/ValueSelector";
import StepSelector from "../common/StepSelector";
import TotalsDisplay from "../common/TotalsDisplay";
import DailyConsumptionChart from "../DailyConsumptionChart/DailyConsumptionChart";
import Loader from "../../common/Loader";
import fetchDailyConsumption from "../../../services/fetchDailyConsumption";
import styles from "./DisplayConsumptionBlock.module.scss";

export default function DisplayConsumptionBlock() {
  const today = new Date().toISOString().slice(0, 10);

  const [date, setDate] = useState(today);
  const [step, setStep] = useState(1);
  const [valueType, setValueType] = useState("average_watt");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      setError(null);
      try {
        const result = await fetchDailyConsumption(date, step);
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

  function renderChart() {
    if (!data) return null;

    return (
      <DailyConsumptionChart
        data={data.data}
        chartType={valueType === "average_watt" ? "line" : "area"}
        valueKey={valueType}
      />
    );
  }

  return (
    <div className={styles.block}>
      <div className={styles.selectors}>
        <ValueSelector value={valueType} onChange={setValueType} />
        <DatePicker value={date} onChange={setDate} />
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
