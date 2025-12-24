import { fetchJson } from './fetchJson';
import DailyConsumption from '../models/DailyConsumption';
import { mockDailyConsumption1 } from '../mocks/mockDailyConsumption1';
import { mockDailyConsumption30 } from '../mocks/mockDailyConsumption30';
import { mockDailyConsumption60 } from '../mocks/mockDailyConsumption60';

const USE_MOCK = false; // Use true for dev

const MOCKS_BY_STEP = {
  1: mockDailyConsumption1,
  30: mockDailyConsumption30,
  60: mockDailyConsumption60,
};

async function fetchDailyConsumption(date, step = 1) {
  if (USE_MOCK) {
    const mockData = MOCKS_BY_STEP[step];
    if (!mockData) {
      throw new Error(`No mock data available for step: ${step}`);
    }
    return new DailyConsumption(
      mockData.date,
      mockData.step,
      mockData.data,
      mockData.totals
    );
  }

  if (!DailyConsumption.ALLOWED_STEPS.includes(step)) {
    throw new Error(
      `Invalid step value: ${step}. Allowed values: ${DailyConsumption.ALLOWED_STEPS.join(
        ', '
      )}`
    );
  }

  const params = new URLSearchParams({ date, step: step.toString() });

  try {
    const data = await fetchJson(`/api/consumption/daily/?${params}`);
    if (!data || typeof data !== 'object') {
      throw new Error('Invalid response format from API');
    }
    return new DailyConsumption(data.date, data.step, data.data, data.totals);
  } catch (error) {
    console.error('Error fetching daily consumption:', error);
    throw error;
  }
}

export default fetchDailyConsumption;
