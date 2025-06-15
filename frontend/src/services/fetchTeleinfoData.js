import { fetchJson } from "./fetchJson";
import TeleinfoData from "../models/TeleinfoData";

async function fetchTeleinfoData() {
  const rawData = await fetchJson("/api/teleinfo/data/");
  return new TeleinfoData(rawData);
}

export default fetchTeleinfoData;
