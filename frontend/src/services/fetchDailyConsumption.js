import { fetchJson } from "./fetchJson";
import DailyConsumption from "../models/DailyConsumption";

async function fetchDailyConsumption(date, step = 1) {
  if (!DailyConsumption.ALLOWED_STEPS.includes(step)) {
    throw new Error(
      `Invalid step value: ${step}. Allowed values: ${DailyConsumption.ALLOWED_STEPS.join(
        ", "
      )}`
    );
  }

  const params = new URLSearchParams({ date, step: step.toString() });

  try {
    const data = await fetchJson(`/api/consumption/daily/?${params}`);

    if (!data || typeof data !== "object") {
      throw new Error("Invalid response format from API");
    }

    return new DailyConsumption(data.date, data.step, data.data, data.totals);
  } catch (error) {
    console.error("Error fetching daily indexes:", error);
    throw error;
  }
}

export default fetchDailyConsumption;
