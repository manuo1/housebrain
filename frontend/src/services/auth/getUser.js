const API_URL = '/api/auth';

export default async function getUser(token = null) {
  const headers = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_URL}/me/`, {
    method: 'GET',
    credentials: 'include',
    headers,
  });

  if (!res.ok) {
    throw new Error('Not authenticated');
  }

  return await res.json(); // { username: "..." }
}
