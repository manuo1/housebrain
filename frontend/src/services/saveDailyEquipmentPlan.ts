import fetchWithAuth, { RefreshCallback } from "./fetchWithAuth";
import DailyEquipmentPlan, { Slot } from "../models/DailyEquipmentPlan";

interface BackendSlot {
  start: string;
  end: string;
  type: "onoff" | "temp";
  value: string | number | null;
}

interface BackendPlan {
  type: string;
  id: number | null;
  date: string | null;
  slots: BackendSlot[];
}

interface BackendPayload {
  plans: BackendPlan[];
}

export interface ChangedEquipment {
  type: string;
  id: number;
  name: string;
}

export interface SaveDailyEquipmentPlanResult {
  created: number;
  updated: number;
  changed_equipments: ChangedEquipment[];
}

function determineSlotType(value: Slot["value"]): "onoff" | "temp" {
  if (value === "on" || value === "off") return "onoff";
  if (typeof value === "number" || (typeof value === "string" && !isNaN(parseFloat(value)))) return "temp";
  return "onoff";
}

function transformPlanForBackend(dailyPlan: DailyEquipmentPlan): BackendPayload {
  const plans: BackendPlan[] = dailyPlan.equipments.map((equipment) => ({
    type: equipment.type,
    id: equipment.id,
    date: dailyPlan.date,
    slots: equipment.slots.map((slot) => {
      const type = determineSlotType(slot.value);
      const value = type === "temp" ? parseFloat(String(slot.value)) : slot.value;
      return { start: slot.start, end: slot.end, type, value };
    }),
  }));
  return { plans };
}

export default async function saveDailyEquipmentPlan(
  dailyPlan: DailyEquipmentPlan,
  accessToken: string,
  refreshCallback: RefreshCallback
): Promise<SaveDailyEquipmentPlanResult> {
  const payload = transformPlanForBackend(dailyPlan);

  const response = await fetchWithAuth(
    "/api/planning/plans/daily/",
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
