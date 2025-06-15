import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import DailyConsumptionChart from "../components/DailyConsumptionChart";
import styles from "./DailyConsumption.module.scss";
import fetchDailyIndexes from "../services/fetchDailyIndexes";

export default function DailyConsumption() {
  const { date } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const isValidDate = /^\d{4}-\d{2}-\d{2}$/.test(date);
    if (!isValidDate) {
      const today = new Date().toISOString().slice(0, 10);
      navigate(`/daily-consumption/${today}`, { replace: true });
      return;
    }

    setLoading(true);
    setError(null);
    fetchDailyIndexes(date)
      .then(setData)
      .catch((err) => setError(err.message || "Failed to fetch data"))
      .finally(() => setLoading(false));
  }, [date, navigate]);

  return (
    <div className={styles.container}>
      <h1>Daily Consumption for {date}</h1>
      {loading && <p>Loading data...</p>}
      {error && <p className={styles.error}>Error: {error}</p>}
      {data && !loading && !error && <DailyConsumptionChart data={data} />}
    </div>
  );
}
