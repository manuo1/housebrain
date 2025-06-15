import {
  TELEINFO_LABELS,
  TELEINFO_UNITS,
} from "../constants/teleinfoConstants";

function formatValue(key, value) {
  if (value === null || value === undefined) return "N/A";
  const unit = TELEINFO_UNITS[key];
  return unit ? `${value} ${unit}` : value;
}

function formatOtherData(otherData) {
  const formatted = {};
  for (const [key, value] of Object.entries(otherData)) {
    const label = TELEINFO_LABELS[key] ?? key;
    formatted[label] = formatValue(key, value);
  }
  return formatted;
}

export { formatValue, formatOtherData };
