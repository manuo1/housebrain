import fetchWithAuth from "./fetchWithAuth";
import DailyHeatingPlan from "../models/DailyHeatingPlan";
import mockDailyHeatingPlan from "../mocks/mockDailyHeatingPlan";

const USE_MOCK = true;

type RefreshCallback = () => Promise<string>;

interface AiModifyPayload {
  date: string;
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
    "/api/heating/plans/ai-modify/",
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
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }

  const rawData = await response.json();
  return new DailyHeatingPlan(rawData);
}
