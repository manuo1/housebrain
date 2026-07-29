import { fetchJson } from "./fetchJson";
import HeatingCalendar from "../models/HeatingCalendar";

async function fetchHeatingCalendar(year?: number, month?: number): Promise<HeatingCalendar> {
  const params = new URLSearchParams();

  if (year != null) {
    params.append("year", String(year));
  }

  if (month != null) {
    params.append("month", String(month));
  }

  const rawData = await fetchJson<Record<string, unknown>>(`/api/heating/calendar/?${params.toString()}`);
  return new HeatingCalendar(rawData);
}

export default fetchHeatingCalendar;
