import { fetchJson } from "./fetchJson";
import DailyIndexes from "../models/DailyIndexes";

async function fetchDailyIndexes(date, step = 1) {
  const params = new URLSearchParams({ step: step.toString() });
  const data = await fetchJson(`/api/consumption/${date}/?${params}`);
  return new DailyIndexes(data.date, data.step, data.data, data.totals);
}

export default fetchDailyIndexes;
