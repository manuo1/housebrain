type RefreshCallback = () => Promise<string>;

export default async function fetchWithAuth(
  url: string,
  options: RequestInit = {},
  refreshCallback?: RefreshCallback
): Promise<Response> {
  let response = await fetch(url, {
    ...options,
    credentials: "include",
  });

  if (response.status === 401 && refreshCallback) {
    try {
      const newAccessToken = await refreshCallback();

      const newHeaders: Record<string, string> = {
        ...(options.headers as Record<string, string>),
        Authorization: `Bearer ${newAccessToken}`,
      };

      response = await fetch(url, {
        ...options,
        headers: newHeaders,
        credentials: "include",
      });
    } catch (refreshError) {
      console.error("Token refresh failed:", refreshError);
      throw new Error("Session expired. Please login again.");
    }
  }

  return response;
}
