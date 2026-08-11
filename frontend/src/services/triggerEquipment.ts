import fetchWithAuth, { RefreshCallback } from "./fetchWithAuth";

export default async function triggerEquipment(
  equipmentId: string,
  accessToken: string,
  refreshCallback: RefreshCallback
): Promise<void> {
  const response = await fetchWithAuth(
    `/api/equipment/${equipmentId}/trigger/`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    },
    refreshCallback
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    const message = Array.isArray(error)
      ? error.join(" ")
      : error.detail || `Erreur ${response.status}`;
    throw new Error(message);
  }
}
