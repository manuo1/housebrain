type ValueType = "temp" | "onoff";

export const getValueType = (val: string): ValueType | null => {
  if (val === "on" || val === "off") return "onoff";
  const num = parseFloat(val);
  if (!isNaN(num)) return "temp";
  return null;
};

export const isOnOff = (value: string): boolean => {
  const lower = value.toLowerCase();
  return lower === "on" || lower === "off";
};

export const isTemperature = (value: string): boolean => {
  const tempValue = Number(value);
  return !isNaN(tempValue);
};

// Get CSS class for slot based on value
export const getSlotClass = (value: string, styles: Record<string, string>): string => {
  const lower = value.toLowerCase();

  if (isOnOff(value)) {
    return lower === "on" ? styles.on : styles.off;
  }

  if (isTemperature(value)) {
    const temp = Math.round(Number(value));
    if (temp < 16) return styles.tempCold;
    if (temp > 24) return styles.tempHot;
    return styles[`temp${temp}`] || "";
  }

  return "";
};

export const getLabel = (value: string): string => {
  const lower = value.toLowerCase();
  if (isOnOff(value)) return lower === "on" ? "ON" : "OFF";
  if (isTemperature(value)) return `${Number(value)}°`;
  return value;
};
