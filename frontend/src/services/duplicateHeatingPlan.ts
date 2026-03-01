import fetchWithAuth from "./fetchWithAuth";

type RefreshCallback = () => Promise<string>;

export default async function duplicateHeatingPlan(
  duplicationData: Record<string, unknown>,
  accessToken: string,
  refreshCallback: RefreshCallback
): Promise<unknown> {
  const response = await fetchWithAuth(
    "/api/heating/plans/duplicate/",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify(duplicationData),
    },
    refreshCallback
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}
