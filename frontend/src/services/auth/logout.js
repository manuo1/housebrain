const API_URL = '/api/auth';

export default async function logout() {
  const res = await fetch(`${API_URL}/logout/`, {
    method: 'POST',
    credentials: 'include',
  });

  if (!res.ok) {
    throw new Error('Logout failed');
  }

  return await res.json();
}
