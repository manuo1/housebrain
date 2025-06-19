import React, { useEffect, useState, useCallback } from "react";
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
  const [currentStep, setCurrentStep] = useState(1);

  const selectedDate = date || new Date().toISOString().slice(0, 10);

  // Fonction pour charger les données avec un step spécifique
  const loadData = useCallback(async (date, step = 1) => {
    setLoading(true);
    setError(null);

    try {
      const result = await fetchDailyIndexes(date, step);
      setData(result);
      setCurrentStep(step);
    } catch (err) {
      setError(err.message || "Failed to fetch data");
    } finally {
      setLoading(false);
    }
  }, []);

  // Chargement initial des données
  useEffect(() => {
    const isValidDate = /^\d{4}-\d{2}-\d{2}$/.test(selectedDate);
    if (!isValidDate) {
      const currentDay = new Date().toISOString().slice(0, 10);
      navigate(`/daily-consumption/${currentDay}`, { replace: true });
      return;
    }

    loadData(selectedDate, currentStep);
  }, [selectedDate, loadData, navigate, currentStep]);

  // Gestion du changement de date
  function handleDateChange(newDate) {
    navigate(`/daily-consumption/${newDate}`);
  }

  // Gestion du changement de step (résolution)
  const handleStepChange = useCallback(
    (newStep) => {
      if (newStep !== currentStep) {
        loadData(selectedDate, newStep);
      }
    },
    [selectedDate, currentStep, loadData]
  );

  return (
    <div className={styles.container}>
      <DatePicker
        value={selectedDate}
        onChange={handleDateChange}
        max={new Date().toISOString().slice(0, 10)}
      />

      {error && <p className={styles.error}>Error: {error}</p>}

      {(data || loading) && (
        <DailyConsumptionChart
          data={data}
          onStepChange={handleStepChange}
          loading={loading}
        />
      )}
    </div>
  );
}
