import {
  TELEINFO_LABELS,
  TELEINFO_UNITS,
} from "../constants/teleinfoConstants";

function formatValue(key: string, value: string | number | null | undefined): string {
  if (value === null || value === undefined) return "N/A";
  const unit = TELEINFO_UNITS[key];
  return unit ? `${value} ${unit}` : String(value);
}

function formatOtherData(otherData: Record<string, string | number | null | undefined>): Record<string, string> {
  const formatted: Record<string, string> = {};
  for (const [key, value] of Object.entries(otherData)) {
    const label = TELEINFO_LABELS[key] ?? key;
    formatted[label] = formatValue(key, value);
  }
  return formatted;
}

export { formatValue, formatOtherData };
