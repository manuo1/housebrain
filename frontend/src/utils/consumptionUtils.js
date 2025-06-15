const DEFAULT_VOLTAGE = 230;

export function ampereToWatt(intensity) {
  if (typeof intensity !== "number") return null;
  return intensity * DEFAULT_VOLTAGE;
}
