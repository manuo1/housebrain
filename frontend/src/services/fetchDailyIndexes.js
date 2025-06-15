import { fetchJson } from "./fetchJson";
import DailyIndexes from "../models/DailyIndexes";

async function fetchDailyIndexes(date) {
  const data = await fetchJson(`/api/consumption/wh/${date}/`);
  return new DailyIndexes(data.date, data.watt_hours, data.totals);
}

export default fetchDailyIndexes;
