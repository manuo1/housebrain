import { fetchJson } from "./fetchJson";
import EquipmentCalendar from "../models/EquipmentCalendar";

async function fetchEquipmentCalendar(year?: number, month?: number): Promise<EquipmentCalendar> {
  const params = new URLSearchParams();

  if (year != null) {
    params.append("year", String(year));
  }

  if (month != null) {
    params.append("month", String(month));
  }

  const rawData = await fetchJson<Record<string, unknown>>(`/api/planning/calendar/?${params.toString()}`);
  return new EquipmentCalendar(rawData);
}

export default fetchEquipmentCalendar;
