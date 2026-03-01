import { DEFAULT_VOLTAGE } from "../constants/teleinfoConstants";

export function ampereToWatt(intensity: number): number | null {
  if (typeof intensity !== "number") return null;
  return intensity * DEFAULT_VOLTAGE;
}
