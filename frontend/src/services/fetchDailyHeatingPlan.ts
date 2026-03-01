import { fetchJson } from "./fetchJson";
import DailyHeatingPlan from "../models/DailyHeatingPlan";
import mockDailyHeatingPlan from "../mocks/mockDailyHeatingPlan";

const USE_MOCK = false;

async function fetchDailyHeatingPlan(date: string): Promise<DailyHeatingPlan> {
  if (USE_MOCK) {
    return mockDailyHeatingPlan;
  }

  const rawData = await fetchJson<Record<string, unknown>>(`/api/heating/plans/daily/?date=${date}`);
  return new DailyHeatingPlan(rawData);
}

export default fetchDailyHeatingPlan;
