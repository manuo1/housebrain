import { AUTH_API_URL } from "../../constants/authConstants";

interface RefreshResponse {
  access: string;
}

export default async function refresh(): Promise<RefreshResponse> {
  const res = await fetch(`${AUTH_API_URL}/refresh/`, {
    method: "POST",
    credentials: "include",
  });

  if (!res.ok) {
    throw new Error("Refresh failed");
  }

  return await res.json();
}
