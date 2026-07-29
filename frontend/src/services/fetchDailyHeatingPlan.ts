import { fetchJson } from "./fetchJson";
import DailyHeatingPlan from "../models/DailyHeatingPlan";

async function fetchDailyHeatingPlan(date: string): Promise<DailyHeatingPlan> {
  const rawData = await fetchJson<Record<string, unknown>>(`/api/heating/plans/daily/?date=${date}`);
  return new DailyHeatingPlan(rawData);
}

export default fetchDailyHeatingPlan;
