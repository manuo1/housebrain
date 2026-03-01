import { fetchJson } from "./fetchJson";
import HeatingCalendar from "../models/HeatingCalendar";
import mockHeatingCalendar from "../mocks/mockHeatingCalendar";

const USE_MOCK = false;

async function fetchHeatingCalendar(year?: number, month?: number): Promise<HeatingCalendar> {
  if (USE_MOCK) {
    return mockHeatingCalendar;
  }

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
