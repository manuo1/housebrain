/**
 * Convert time string (HH:MM) to total minutes
 * @param {string} timeStr - Time in format "HH:MM"
 * @returns {number} Total minutes since midnight
 */
export const timeToMinutes = (timeStr) => {
  const [hours, minutes] = timeStr.split(':').map(Number);
  return hours * 60 + minutes;
};

/**
 * Convert minutes to time string (HH:MM)
 * @param {number} minutes - Total minutes since midnight
 * @returns {string} Time in format "HH:MM"
 */
export const minutesToTime = (minutes) => {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${String(hours).padStart(2, '0')}:${String(mins).padStart(2, '0')}`;
};

/**
 * Convert time string (HH:MM) to percentage of day
 * @param {string} timeStr - Time in format "HH:MM"
 * @returns {number} Percentage of day (0-100)
 */
export const timeToPercent = (timeStr) => {
  const [hours, minutes] = timeStr.split(':').map(Number);
  const totalMinutes = hours * 60 + minutes;
  return (totalMinutes / 1440) * 100; // 1440 = 24h * 60min
};

/**
 * Convert percentage of day to time string (HH:MM)
 * @param {number} percent - Percentage of day (0-100)
 * @returns {string} Time in format "HH:MM"
 */
export const percentToTime = (percent) => {
  const totalMinutes = Math.round((percent / 100) * 1440);
  return minutesToTime(totalMinutes);
};

/**
 * Calculate position and width for slot display
 * @param {Object} slot - Slot with start and end times
 * @returns {Object} Object with left and width as percentage strings
 */
export const calculateSlotPosition = (slot) => {
  const startPercent = timeToPercent(slot.start);
  const endPercent = timeToPercent(slot.end);
  const widthPercent = endPercent - startPercent;

  return {
    left: `${startPercent}%`,
    width: `${widthPercent}%`,
  };
};
