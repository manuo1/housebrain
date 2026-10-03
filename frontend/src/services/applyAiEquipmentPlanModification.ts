import fetchWithAuth, { RefreshCallback } from "./fetchWithAuth";
import DailyEquipmentPlan from "../models/DailyEquipmentPlan";

interface AiModifyPayload {
  instruction: string;
  plan: object;
}

export default async function applyAiEquipmentPlanModification(
  payload: AiModifyPayload,
  accessToken: string,
  refreshCallback: RefreshCallback
): Promise<DailyEquipmentPlan> {
  const response = await fetchWithAuth(
    "/api/ai/equipment/modify/",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify(payload),
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

  const rawData = await response.json();
  return new DailyEquipmentPlan(rawData);
}
