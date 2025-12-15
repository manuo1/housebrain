import fetchWithAuth from './fetchWithAuth';

/**
 * Determine slot type based on value
 */
function determineSlotType(value) {
  if (value === 'on' || value === 'off') {
    return 'onoff';
  }
  if (typeof value === 'number' || !isNaN(parseFloat(value))) {
    return 'temp';
  }
  return 'onoff';
}

/**
 * Transform dailyPlan to backend format
 */
function transformPlanForBackend(dailyPlan) {
  const plans = dailyPlan.rooms.map((room) => ({
    room_id: room.id,
    date: dailyPlan.date,
    slots: room.slots.map((slot) => {
      const type = determineSlotType(slot.value);
      const value = type === 'temp' ? parseFloat(slot.value) : slot.value;

      return {
        start: slot.start,
        end: slot.end,
        type,
        value,
      };
    }),
  }));

  return { plans };
}

/**
 * Save daily heating plan to backend
 * @param {Object} dailyPlan - The daily heating plan to save
 * @param {string} accessToken - JWT access token
 * @param {Function} refreshCallback - Function to refresh token
 * @returns {Promise<Object>} - Response from backend
 */
export default async function saveDailyHeatingPlan(
  dailyPlan,
  accessToken,
  refreshCallback
) {
  const payload = transformPlanForBackend(dailyPlan);

  const response = await fetchWithAuth(
    '/api/heating/plans/daily/',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify(payload),
    },
    refreshCallback
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}
