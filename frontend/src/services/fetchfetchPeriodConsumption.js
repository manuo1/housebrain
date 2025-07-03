import { fetchJson } from "./fetchJson";
import PeriodConsumption from "../models/PeriodConsumption";

export default async function fetchPeriodConsumption(
  startDate,
  endDate,
  period = "day"
) {
  const params = new URLSearchParams({
    start_date: startDate,
    end_date: endDate,
    period,
  });

  const data = await fetchJson(`/api/consumption/by-period/?${params}`);
  return new PeriodConsumption(data);
}
