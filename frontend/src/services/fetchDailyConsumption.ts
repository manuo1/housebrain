import { fetchJson } from "./fetchJson";
import DailyConsumption, { DailyConsumptionElementRaw, TotalByLabelRaw } from "../models/DailyConsumption";

interface DailyConsumptionResponse {
  date: string;
  step: number;
  data: DailyConsumptionElementRaw[];
  totals: Record<string, TotalByLabelRaw>;
}

async function fetchDailyConsumption(date: string, step: number = 1): Promise<DailyConsumption> {
  if (!DailyConsumption.ALLOWED_STEPS.includes(step)) {
    throw new Error(`Invalid step value: ${step}. Allowed values: ${DailyConsumption.ALLOWED_STEPS.join(", ")}`);
  }

  const params = new URLSearchParams({ date, step: step.toString() });

  try {
    const data = await fetchJson<DailyConsumptionResponse>(`/api/consumption/daily/?${params}`);
    if (!data || typeof data !== "object") {
      throw new Error("Invalid response format from API");
    }
    return new DailyConsumption(data.date, data.step, data.data, data.totals);
  } catch (error) {
    console.error("Error fetching daily consumption:", error);
    throw error;
  }
}

export default fetchDailyConsumption;
