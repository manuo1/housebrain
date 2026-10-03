import { useState, useEffect, useCallback, useRef } from "react";
import fetchDailyEquipmentPlan from "../../services/fetchDailyEquipmentPlan";
import saveDailyEquipmentPlan, { ChangedEquipment } from "../../services/saveDailyEquipmentPlan";
import { useAuth } from "../../contexts/useAuth";
import DailyEquipmentPlan from "../../models/DailyEquipmentPlan";

interface UseEquipmentPlanHistoryResult {
  dailyPlan: DailyEquipmentPlan | null;
  loading: boolean;
  canUndo: boolean;
  hasChanges: boolean;
  applyChange: (newPlan: DailyEquipmentPlan) => void;
  undo: () => void;
  save: () => Promise<ChangedEquipment[]>;
}

export function useEquipmentPlanHistory(selectedDate: string | null): UseEquipmentPlanHistoryResult {
  const { accessToken, refresh } = useAuth();
  const [dailyPlan, setDailyPlan] = useState<DailyEquipmentPlan | null>(null);
  const [history, setHistory] = useState<DailyEquipmentPlan[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const dailyPlanRef = useRef<DailyEquipmentPlan | null>(null);
  dailyPlanRef.current = dailyPlan;

  useEffect(() => {
    if (!selectedDate) return;

    async function loadDailyPlan() {
      setLoading(true);
      try {
        const data = await fetchDailyEquipmentPlan(selectedDate!);
        setDailyPlan(data);
        setHistory([]);
      } catch (error) {
        console.error("Error loading daily plan:", error);
      } finally {
        setLoading(false);
      }
    }
    loadDailyPlan();
  }, [selectedDate]);

  const applyChange = useCallback((newPlan: DailyEquipmentPlan) => {
    setHistory((prev) => [...prev, dailyPlanRef.current!]);
    setDailyPlan(newPlan);
  }, []);

  const undo = useCallback(() => {
    if (history.length === 0) return;
    const previousState = history[history.length - 1];
    setDailyPlan(previousState);
    setHistory((prev) => prev.slice(0, -1));
  }, [history]);

  const save = useCallback(async (): Promise<ChangedEquipment[]> => {
    if (!accessToken) throw new Error("No access token available");

    try {
      const result = await saveDailyEquipmentPlan(dailyPlanRef.current!, accessToken, refresh);
      const data = await fetchDailyEquipmentPlan(selectedDate!);
      setDailyPlan(data);
      setHistory([]);
      return result.changed_equipments;
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
    save,
  };
}
