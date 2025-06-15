import { DEFAULT_VOLTAGE } from "../constants/teleinfoConstants";

export function ampereToWatt(intensity) {
  if (typeof intensity !== "number") return null;
  return intensity * DEFAULT_VOLTAGE;
}
