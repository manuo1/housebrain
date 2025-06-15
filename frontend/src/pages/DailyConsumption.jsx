import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import DailyConsumptionChart from "../components/DailyConsumptionChart";
import DatePicker from "../components/DatePicker";
import styles from "./DailyConsumption.module.scss";
import fetchDailyIndexes from "../services/fetchDailyIndexes";

export default function DailyConsumption() {
  const { date } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const selectedDate = date || new Date().toISOString().slice(0, 10);

  useEffect(() => {
    const isValidDate = /^\d{4}-\d{2}-\d{2}$/.test(selectedDate);
    if (!isValidDate) {
      const curent_day = new Date().toISOString().slice(0, 10);
      navigate(`/daily-consumption/${curent_day}`, { replace: true });
      return;
    }

    setLoading(true);
    setError(null);
    fetchDailyIndexes(selectedDate)
      .then(setData)
      .catch((err) => setError(err.message || "Failed to fetch data"))
      .finally(() => setLoading(false));
  }, [selectedDate, navigate]);

  function handleDateChange(newDate) {
    navigate(`/daily-consumption/${newDate}`);
  }

  return (
    <div className={styles.container}>
      <h1>Daily Consumption for {selectedDate}</h1>
      <DatePicker
        value={selectedDate}
        onChange={handleDateChange}
        max={new Date().toISOString().slice(0, 10)}
      />
      {loading && <p>Loading data...</p>}
      {error && <p className={styles.error}>Error: {error}</p>}
      {data && !loading && !error && <DailyConsumptionChart data={data} />}
    </div>
  );
}
