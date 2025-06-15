import { fetchJson } from "./fetchJson";

async function fetchTeleinfoData() {
  const data = await fetchJson("/api/teleinfo/data/");
  return data;
}

export default fetchTeleinfoData;
