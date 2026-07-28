import { AUTH_API_URL } from "../../constants/authConstants";

export default async function logout(): Promise<void> {
  const res = await fetch(`${AUTH_API_URL}/logout/`, {
    method: "POST",
    credentials: "include",
  });

  if (!res.ok) {
    throw new Error("Logout failed");
  }

  await res.json();
}
