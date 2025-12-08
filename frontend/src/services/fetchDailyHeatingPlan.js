import { fetchJson } from './fetchJson';
import DailyHeatingPlan from '../models/DailyHeatingPlan';
import mockDailyHeatingPlan from '../mocks/mockDailyHeatingPlan';

const USE_MOCK = false; // Use true for dev

/**
 * Fetch daily heating plan for a specific date
 * @param {string} date - Format YYYY-MM-DD
 * @returns {Promise<DailyHeatingPlan>}
 */
async function fetchDailyHeatingPlan(date) {
  if (USE_MOCK) {
    return mockDailyHeatingPlan;
  }

  const rawData = await fetchJson(`/api/heating/plan/${date}/`);
  return new DailyHeatingPlan(rawData);
}

export default fetchDailyHeatingPlan;
