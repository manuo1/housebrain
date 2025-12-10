const API_URL = '/api/auth';

export default async function refresh() {
  const res = await fetch(`${API_URL}/refresh/`, {
    method: 'POST',
    credentials: 'include',
  });

  if (!res.ok) {
    throw new Error('Refresh failed');
  }

  return await res.json(); // { access: "..." }
}
