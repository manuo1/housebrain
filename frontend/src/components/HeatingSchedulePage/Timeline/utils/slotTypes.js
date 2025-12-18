/**
 * Get value type (temperature or on/off)
 * @param {string} val - Slot value
 * @returns {string|null} 'temp', 'onoff', or null
 */
export const getValueType = (val) => {
  if (val === 'on' || val === 'off') return 'onoff';
  const num = parseFloat(val);
  if (!isNaN(num)) return 'temp';
  return null;
};

/**
 * Check if value is on/off type
 * @param {string} value - Slot value
 * @returns {boolean}
 */
export const isOnOff = (value) => {
  const lower = value.toLowerCase();
  return lower === 'on' || lower === 'off';
};

/**
 * Check if value is temperature type
 * @param {string} value - Slot value
 * @returns {boolean}
 */
export const isTemperature = (value) => {
  const tempValue = Number(value);
  return !isNaN(tempValue);
};

/**
 * Get CSS class for slot based on value
 * @param {string} value - Slot value
 * @param {Object} styles - CSS modules styles object
 * @returns {string} CSS class name
 */
export const getSlotClass = (value, styles) => {
  const lower = value.toLowerCase();

  if (isOnOff(value)) {
    return lower === 'on' ? styles.on : styles.off;
  }

  if (isTemperature(value)) {
    const temp = Math.round(Number(value));

    if (temp < 16) return styles.tempCold;
    if (temp > 24) return styles.tempHot;

    return styles[`temp${temp}`] || '';
  }

  return '';
};

/**
 * Get display label for slot
 * @param {string} value - Slot value
 * @returns {string} Display label
 */
export const getLabel = (value) => {
  const lower = value.toLowerCase();

  if (isOnOff(value)) {
    return lower === 'on' ? 'ON' : 'OFF';
  }

  if (isTemperature(value)) {
    return `${Number(value)}°`;
  }

  return value;
};
