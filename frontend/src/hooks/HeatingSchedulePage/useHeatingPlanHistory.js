import { useState, useEffect, useCallback, useRef } from 'react';
import fetchDailyHeatingPlan from '../../services/fetchDailyHeatingPlan';
import saveDailyHeatingPlan from '../../services/saveDailyHeatingPlan';
import { useAuth } from '../../contexts/useAuth';

export function useHeatingPlanHistory(selectedDate) {
  const { accessToken, refresh } = useAuth();
  const [dailyPlan, setDailyPlan] = useState(null);
  const [initialPlan, setInitialPlan] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  // Ref pour avoir toujours la dernière valeur de dailyPlan
  const dailyPlanRef = useRef(null);
  dailyPlanRef.current = dailyPlan;

  // Fetch data when date changes
  useEffect(() => {
    if (!selectedDate) return;

    async function loadDailyPlan() {
      setLoading(true);
      try {
        const data = await fetchDailyHeatingPlan(selectedDate);
        setDailyPlan(data);
        setInitialPlan(data);
        setHistory([]);
      } catch (error) {
        console.error('Error loading daily plan:', error);
      } finally {
        setLoading(false);
      }
    }
    loadDailyPlan();
  }, [selectedDate]);

  // Apply a change (push current state to history, update dailyPlan)
  const applyChange = useCallback((newPlan) => {
    setHistory((prev) => [...prev, dailyPlanRef.current]);
    setDailyPlan(newPlan);
  }, []);

  // Undo last change
  const undo = useCallback(() => {
    if (history.length === 0) return;

    const previousState = history[history.length - 1];
    setDailyPlan(previousState);
    setHistory((prev) => prev.slice(0, -1));
  }, [history]);

  // Reset to initial state
  const reset = useCallback(() => {
    setDailyPlan(initialPlan);
    setHistory([]);
  }, [initialPlan]);

  // Save changes (POST to backend, then reload)
  const save = useCallback(async () => {
    if (!accessToken) {
      throw new Error('No access token available');
    }

    try {
      // Utiliser la ref pour avoir la valeur actuelle et passer refresh
      await saveDailyHeatingPlan(dailyPlanRef.current, accessToken, refresh);

      // Reload from backend
      const data = await fetchDailyHeatingPlan(selectedDate);
      setDailyPlan(data);
      setInitialPlan(data);
      setHistory([]);
    } catch (error) {
      console.error('Error saving daily plan:', error);
      throw error;
    }
  }, [accessToken, refresh, selectedDate]);

  return {
    dailyPlan,
    loading,
    canUndo: history.length > 0,
    hasChanges: history.length > 0,
    applyChange,
    undo,
    reset,
    save,
  };
}
