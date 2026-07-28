import { AUTH_API_URL } from "../../constants/authConstants";

interface GetUserResponse {
  username: string;
}

export default async function getUser(token: string | null = null): Promise<GetUserResponse> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${AUTH_API_URL}/me/`, {
    method: "GET",
    credentials: "include",
    headers,
  });

  if (!res.ok) {
    throw new Error("Not authenticated");
  }

  return await res.json();
}
