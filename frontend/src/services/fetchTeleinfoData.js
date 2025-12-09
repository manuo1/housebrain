import { fetchJson } from './fetchJson';
import TeleinfoData from '../models/TeleinfoData';
import mockTeleinfoData from '../mocks/mockTeleinfoData';

const USE_MOCK = false; // Use true for dev

async function fetchTeleinfoData() {
  if (USE_MOCK) {
    return mockTeleinfoData;
  }
  const rawData = await fetchJson('/api/teleinfo/data/');
  return new TeleinfoData(rawData);
}

export default fetchTeleinfoData;
