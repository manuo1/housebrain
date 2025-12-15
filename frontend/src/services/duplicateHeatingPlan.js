import fetchWithAuth from './fetchWithAuth';

/**
 * Duplicate heating plan to multiple dates
 * @param {Object} duplicationData - The duplication payload
 * @param {string} accessToken - JWT access token
 * @param {Function} refreshCallback - Function to refresh token
 * @returns {Promise<Object>} - Response from backend
 */
export default async function duplicateHeatingPlan(
  duplicationData,
  accessToken,
  refreshCallback
) {
  const response = await fetchWithAuth(
    '/api/heating/plans/duplicate/',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify(duplicationData),
    },
    refreshCallback
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}
