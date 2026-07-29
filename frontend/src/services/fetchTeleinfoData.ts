import { fetchJson } from "./fetchJson";
import TeleinfoData from "../models/TeleinfoData";

async function fetchTeleinfoData(): Promise<TeleinfoData> {
  const rawData = await fetchJson<Record<string, string | number | null>>("/api/teleinfo/data/");
  return new TeleinfoData(rawData);
}

export default fetchTeleinfoData;
