const API_URL = '/api/auth';

export default async function login(username, password) {
  const res = await fetch(`${API_URL}/login/`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });

  if (!res.ok) {
    throw new Error('Invalid credentials');
  }

  return await res.json(); // { access: "..." }
}
