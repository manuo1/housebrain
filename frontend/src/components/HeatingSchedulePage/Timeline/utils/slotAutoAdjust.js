import { timeToMinutes, minutesToTime } from './slotCalculations';

/**
 * Find slots before and after a given time
 * @param {string} clickTime - Time clicked (HH:MM)
 * @param {Array} slots - Array of existing slots
 * @returns {Object} Object with slotBefore and slotAfter
 */
export const findAdjacentSlots = (clickTime, slots) => {
  const clickMin = timeToMinutes(clickTime);

  let slotBefore = null;
  let slotAfter = null;

  // Sort slots by start time
  const sortedSlots = [...slots].sort((a, b) => {
    return timeToMinutes(a.start) - timeToMinutes(b.start);
  });

  for (const slot of sortedSlots) {
    const slotStart = timeToMinutes(slot.start);
    const slotEnd = timeToMinutes(slot.end);

    if (slotEnd < clickMin) {
      slotBefore = slot;
    } else if (slotStart > clickMin && !slotAfter) {
      slotAfter = slot;
      break;
    }
  }

  return { slotBefore, slotAfter };
};

/**
 * Calculate optimal start and end times for a new slot based on click position
 * @param {string} clickTime - Time clicked (HH:MM)
 * @param {Array} slots - Array of existing slots
 * @returns {Object} Object with start and end times
 */
export const calculateOptimalSlotTimes = (clickTime, slots) => {
  const clickMin = timeToMinutes(clickTime);
  const { slotBefore, slotAfter } = findAdjacentSlots(clickTime, slots);

  let startMin = clickMin;
  let endMin = clickMin + 60; // Default 1 hour

  // If there's a slot before, start 1 minute after it ends
  if (slotBefore) {
    const beforeEnd = timeToMinutes(slotBefore.end);
    startMin = beforeEnd + 1;
  } else {
    // No slot before: start at beginning of day (00:00)
    startMin = 0;
  }

  // If there's a slot after, end 1 minute before it starts
  if (slotAfter) {
    const afterStart = timeToMinutes(slotAfter.start);
    endMin = afterStart - 1;
  } else {
    // No slot after: end at end of day (23:59)
    endMin = 1439;
  }

  return {
    start: minutesToTime(startMin),
    end: minutesToTime(endMin),
  };
};
