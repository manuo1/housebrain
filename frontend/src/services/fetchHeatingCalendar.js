import { fetchJson } from './fetchJson';
import HeatingCalendar from '../models/HeatingCalendar';
import mockHeatingCalendar from '../mocks/mockHeatingCalendar';

const USE_MOCK = false; // Use true for dev

/**
 * Fetch heating calendar for a specific month
 * @param {number} year - Year (e.g., 2025)
 * @param {number} month - Month (1-12)
 * @returns {Promise<HeatingCalendar>}
 */
async function fetchHeatingCalendar(year, month) {
  if (USE_MOCK) {
    return mockHeatingCalendar;
  }

  const rawData = await fetchJson(
    `/api/heating/calendar/${year}-${month.toString().padStart(2, '0')}/`
  );
  return new HeatingCalendar(rawData);
}

export default fetchHeatingCalendar;
