const API_URL = "/api/auth";

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

  const res = await fetch(`${API_URL}/me/`, {
    method: "GET",
    credentials: "include",
    headers,
  });

  if (!res.ok) {
    throw new Error("Not authenticated");
  }

  return await res.json();
}
