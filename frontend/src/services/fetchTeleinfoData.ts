import { fetchJson } from "./fetchJson";
import TeleinfoData from "../models/TeleinfoData";
import mockTeleinfoData from "../mocks/mockTeleinfoData";

const USE_MOCK = false;

async function fetchTeleinfoData(): Promise<TeleinfoData> {
  if (USE_MOCK) {
    return mockTeleinfoData;
  }
  const rawData = await fetchJson<Record<string, string | number | null>>("/api/teleinfo/data/");
  return new TeleinfoData(rawData);
}

export default fetchTeleinfoData;
