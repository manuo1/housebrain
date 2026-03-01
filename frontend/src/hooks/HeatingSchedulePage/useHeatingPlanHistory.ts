import { useState, useEffect, useCallback, useRef } from "react";
import fetchDailyHeatingPlan from "../../services/fetchDailyHeatingPlan";
import saveDailyHeatingPlan from "../../services/saveDailyHeatingPlan";
import { useAuth } from "../../contexts/useAuth";
import DailyHeatingPlan from "../../models/DailyHeatingPlan";

interface UseHeatingPlanHistoryResult {
  dailyPlan: DailyHeatingPlan | null;
  loading: boolean;
  canUndo: boolean;
  hasChanges: boolean;
  applyChange: (newPlan: DailyHeatingPlan) => void;
  undo: () => void;
  reset: () => void;
  save: () => Promise<void>;
}

export function useHeatingPlanHistory(selectedDate: string | null): UseHeatingPlanHistoryResult {
  const { accessToken, refresh } = useAuth();
  const [dailyPlan, setDailyPlan] = useState<DailyHeatingPlan | null>(null);
  const [initialPlan, setInitialPlan] = useState<DailyHeatingPlan | null>(null);
  const [history, setHistory] = useState<DailyHeatingPlan[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const dailyPlanRef = useRef<DailyHeatingPlan | null>(null);
  dailyPlanRef.current = dailyPlan;

  useEffect(() => {
    if (!selectedDate) return;

    async function loadDailyPlan() {
      setLoading(true);
      try {
        const data = await fetchDailyHeatingPlan(selectedDate!);
        setDailyPlan(data);
        setInitialPlan(data);
        setHistory([]);
      } catch (error) {
        console.error("Error loading daily plan:", error);
      } finally {
        setLoading(false);
      }
    }
    loadDailyPlan();
  }, [selectedDate]);

  const applyChange = useCallback((newPlan: DailyHeatingPlan) => {
    setHistory((prev) => [...prev, dailyPlanRef.current!]);
    setDailyPlan(newPlan);
  }, []);

  const undo = useCallback(() => {
    if (history.length === 0) return;
    const previousState = history[history.length - 1];
    setDailyPlan(previousState);
    setHistory((prev) => prev.slice(0, -1));
  }, [history]);

  const reset = useCallback(() => {
    setDailyPlan(initialPlan);
    setHistory([]);
  }, [initialPlan]);

  const save = useCallback(async (): Promise<void> => {
    if (!accessToken) throw new Error("No access token available");

    try {
      await saveDailyHeatingPlan(dailyPlanRef.current!, accessToken, refresh);
      const data = await fetchDailyHeatingPlan(selectedDate!);
      setDailyPlan(data);
      setInitialPlan(data);
      setHistory([]);
    } catch (error) {
      console.error("Error saving daily plan:", error);
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
