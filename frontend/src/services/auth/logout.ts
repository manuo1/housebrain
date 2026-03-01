const API_URL = "/api/auth";

export default async function logout(): Promise<void> {
  const res = await fetch(`${API_URL}/logout/`, {
    method: "POST",
    credentials: "include",
  });

  if (!res.ok) {
    throw new Error("Logout failed");
  }

  await res.json();
}
