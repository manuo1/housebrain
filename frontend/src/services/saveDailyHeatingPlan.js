/**
 * Determine slot type based on value
 * @param {string|number} value - The slot value
 * @returns {string} - 'temp' or 'onoff'
 */
function determineSlotType(value) {
  // Check explicite pour on/off
  if (value === 'on' || value === 'off') {
    return 'onoff';
  }
  // Si c'est un nombre (int ou float), c'est "temp"
  if (typeof value === 'number' || !isNaN(parseFloat(value))) {
    return 'temp';
  }
  // Par défaut onoff (fallback)
  return 'onoff';
}

/**
 * Transform dailyPlan to backend format
 * @param {Object} dailyPlan - The daily heating plan
 * @returns {Object} - Formatted payload for backend
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
 * @returns {Promise<Object>} - Response from backend
 */
export default async function saveDailyHeatingPlan(dailyPlan, accessToken) {
  const payload = transformPlanForBackend(dailyPlan);

  const response = await fetch('/api/heating/plans/daily/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}
