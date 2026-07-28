import { AUTH_API_URL } from "../../constants/authConstants";

interface LoginResponse {
  access: string;
}

export default async function login(username: string, password: string): Promise<LoginResponse> {
  const res = await fetch(`${AUTH_API_URL}/login/`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username, password }),
  });

  if (!res.ok) {
    throw new Error("Invalid credentials");
  }

  return await res.json();
}
