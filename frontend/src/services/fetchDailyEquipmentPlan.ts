import { fetchJson } from "./fetchJson";
import DailyEquipmentPlan from "../models/DailyEquipmentPlan";

async function fetchDailyEquipmentPlan(date: string): Promise<DailyEquipmentPlan> {
  const rawData = await fetchJson<Record<string, unknown>>(`/api/planning/plans/daily/?date=${date}`);
  return new DailyEquipmentPlan(rawData);
}

export default fetchDailyEquipmentPlan;
