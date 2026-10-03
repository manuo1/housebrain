import fetchWithAuth, { RefreshCallback } from "./fetchWithAuth";

export type Role = "user" | "assistant";

export interface Echange {
  role: Role;
  content: string;
}

export type DuplicationStep = "clarify" | "to_validate" | "validate" | "error";

// Equipments are designated by "type:id" keys (ids alone are only unique
// within one equipment type), built and parsed by the backend only.
export interface DuplicationData {
  equipment_keys: string[];
  weekdays: number[];
  start: string | null;
  end: string | null;
}

export interface AiDuplicateResponse {
  echanges: Echange[];
  step: DuplicationStep;
  data: DuplicationData | null;
}

interface AiDuplicatePayload {
  source_date: string;
  echanges: Echange[];
  step: "clarify" | "validate";
  data?: DuplicationData | null;
}

export default async function duplicateEquipmentPlanAi(
  sourceDate: string,
  echanges: Echange[],
  accessToken: string,
  refreshCallback: RefreshCallback,
  step: "clarify" | "validate" = "clarify",
  data?: DuplicationData | null
): Promise<AiDuplicateResponse> {
  const payload: AiDuplicatePayload = { source_date: sourceDate, echanges, step };
  if (data) payload.data = data;

  const response = await fetchWithAuth(
    "/api/ai/equipment/duplicate/",
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

  return response.json();
}
