import fetchWithAuth, { RefreshCallback } from "./fetchWithAuth";

export type Role = "user" | "assistant";

export interface Echange {
  role: Role;
  content: string;
}

export type DuplicationStep = "clarify" | "to_validate" | "validate" | "error";

export interface DuplicationData {
  room_ids: number[];
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

export default async function duplicateHeatingPlanAi(
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
    "/api/ai/heating/duplicate/",
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
