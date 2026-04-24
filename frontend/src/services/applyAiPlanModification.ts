import fetchWithAuth from "./fetchWithAuth";
import DailyHeatingPlan from "../models/DailyHeatingPlan";
import mockDailyHeatingPlan from "../mocks/mockDailyHeatingPlan";

const USE_MOCK = false;

type RefreshCallback = () => Promise<string>;

interface AiModifyPayload {
  instruction: string;
  plan: object;
}

export default async function applyAiPlanModification(
  payload: AiModifyPayload,
  accessToken: string,
  refreshCallback: RefreshCallback
): Promise<DailyHeatingPlan> {
  if (USE_MOCK) {
    return mockDailyHeatingPlan;
  }

  const response = await fetchWithAuth(
    "/api/ai/heating/modify/",
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
    console.log(response)
    const error = await response.json().catch(() => ({}));
    const message = Array.isArray(error)
      ? error.join(" ")
      : error.detail || `Erreur ${response.status}`;
    throw new Error(message);
  }

  const rawData = await response.json();
  return new DailyHeatingPlan(rawData);
}
