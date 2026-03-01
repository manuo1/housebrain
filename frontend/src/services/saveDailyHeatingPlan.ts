import fetchWithAuth from "./fetchWithAuth";
import DailyHeatingPlan, { Slot } from "../models/DailyHeatingPlan";

type RefreshCallback = () => Promise<string>;

interface BackendSlot {
  start: string;
  end: string;
  type: "onoff" | "temp";
  value: string | number | null;
}

interface BackendPlan {
  room_id: number | null;
  date: string | null;
  slots: BackendSlot[];
}

interface BackendPayload {
  plans: BackendPlan[];
}

function determineSlotType(value: Slot["value"]): "onoff" | "temp" {
  if (value === "on" || value === "off") return "onoff";
  if (typeof value === "number" || (typeof value === "string" && !isNaN(parseFloat(value)))) return "temp";
  return "onoff";
}

function transformPlanForBackend(dailyPlan: DailyHeatingPlan): BackendPayload {
  const plans: BackendPlan[] = dailyPlan.rooms.map((room) => ({
    room_id: room.id,
    date: dailyPlan.date,
    slots: room.slots.map((slot) => {
      const type = determineSlotType(slot.value);
      const value = type === "temp" ? parseFloat(String(slot.value)) : slot.value;
      return { start: slot.start, end: slot.end, type, value };
    }),
  }));
  return { plans };
}

export default async function saveDailyHeatingPlan(
  dailyPlan: DailyHeatingPlan,
  accessToken: string,
  refreshCallback: RefreshCallback
): Promise<unknown> {
  const payload = transformPlanForBackend(dailyPlan);

  const response = await fetchWithAuth(
    "/api/heating/plans/daily/",
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

  return response.json();
}
