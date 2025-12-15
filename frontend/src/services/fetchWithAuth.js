/**
 * Fetch wrapper that automatically refreshes token on 401
 * @param {string} url - The URL to fetch
 * @param {Object} options - Fetch options
 * @param {Function} refreshCallback - Function to refresh token (returns new access token)
 * @returns {Promise<Response>}
 */
export default async function fetchWithAuth(
  url,
  options = {},
  refreshCallback
) {
  // First attempt
  let response = await fetch(url, {
    ...options,
    credentials: 'include',
  });

  // If 401, try to refresh token and retry once
  if (response.status === 401 && refreshCallback) {
    try {
      const newAccessToken = await refreshCallback();

      // Retry with new token
      const newHeaders = {
        ...options.headers,
        Authorization: `Bearer ${newAccessToken}`,
      };

      response = await fetch(url, {
        ...options,
        headers: newHeaders,
        credentials: 'include',
      });
    } catch (refreshError) {
      // Refresh failed, return original 401 response
      console.error('Token refresh failed:', refreshError);
      throw new Error('Session expired. Please login again.');
    }
  }

  return response;
}
