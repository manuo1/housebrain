import { timeToMinutes, minutesToTime } from './slotCalculations';
import { validateDuration } from './slotValidation';

/**
 * Find slots that are fully covered by the new slot
 * @param {Object} newSlot - New slot with start and end
 * @param {Array} existingSlots - Array of existing slots
 * @param {number|null} excludeIndex - Index to exclude (when modifying existing slot)
 * @returns {Array} Array of indices of fully covered slots
 */
export const findFullyCoveredSlots = (
  newSlot,
  existingSlots,
  excludeIndex = null
) => {
  const newStart = timeToMinutes(newSlot.start);
  const newEnd = timeToMinutes(newSlot.end);
  const coveredIndices = [];

  existingSlots.forEach((slot, index) => {
    if (index === excludeIndex) return;

    const slotStart = timeToMinutes(slot.start);
    const slotEnd = timeToMinutes(slot.end);

    // Slot is fully covered if new slot starts before/at and ends after/at
    if (newStart <= slotStart && newEnd >= slotEnd) {
      coveredIndices.push(index);
    }
  });

  return coveredIndices;
};

/**
 * Find slot where the new slot starts inside it (partial overlap at start)
 * @param {Object} newSlot - New slot with start and end
 * @param {Array} existingSlots - Array of existing slots
 * @param {number|null} excludeIndex - Index to exclude (when modifying existing slot)
 * @returns {Object|null} Object with slotIndex and adjustedSlot, or null
 */
export const findSlotCoveredAtStart = (
  newSlot,
  existingSlots,
  excludeIndex = null
) => {
  const newStart = timeToMinutes(newSlot.start);
  const newEnd = timeToMinutes(newSlot.end);

  for (let i = 0; i < existingSlots.length; i++) {
    if (i === excludeIndex) continue;

    const slot = existingSlots[i];
    const slotStart = timeToMinutes(slot.start);
    const slotEnd = timeToMinutes(slot.end);

    // New slot starts inside this slot and ends after it
    if (newStart > slotStart && newStart < slotEnd && newEnd >= slotEnd) {
      // Adjust this slot's end to be 1 minute before new slot starts
      const adjustedEnd = minutesToTime(newStart - 1);

      // Check if adjusted slot is still valid (>= 30 min)
      if (!validateDuration(slot.start, adjustedEnd)) {
        // Slot would be too short, mark for removal
        return { slotIndex: i, adjustedSlot: null };
      }

      return {
        slotIndex: i,
        adjustedSlot: { ...slot, end: adjustedEnd },
      };
    }
  }

  return null;
};

/**
 * Find slot where the new slot ends inside it (partial overlap at end)
 * @param {Object} newSlot - New slot with start and end
 * @param {Array} existingSlots - Array of existing slots
 * @param {number|null} excludeIndex - Index to exclude (when modifying existing slot)
 * @returns {Object|null} Object with slotIndex and adjustedSlot, or null
 */
export const findSlotCoveredAtEnd = (
  newSlot,
  existingSlots,
  excludeIndex = null
) => {
  const newStart = timeToMinutes(newSlot.start);
  const newEnd = timeToMinutes(newSlot.end);

  for (let i = 0; i < existingSlots.length; i++) {
    if (i === excludeIndex) continue;

    const slot = existingSlots[i];
    const slotStart = timeToMinutes(slot.start);
    const slotEnd = timeToMinutes(slot.end);

    // New slot starts before this slot and ends inside it
    if (newStart <= slotStart && newEnd >= slotStart && newEnd < slotEnd) {
      // Adjust this slot's start to be 1 minute after new slot ends
      const adjustedStart = minutesToTime(newEnd + 1);

      // Check if adjusted slot is still valid (>= 30 min)
      if (!validateDuration(adjustedStart, slot.end)) {
        // Slot would be too short, mark for removal
        return { slotIndex: i, adjustedSlot: null };
      }

      return {
        slotIndex: i,
        adjustedSlot: { ...slot, start: adjustedStart },
      };
    }
  }

  return null;
};

/**
 * Find slot where the new slot is completely inside it (needs splitting)
 * @param {Object} newSlot - New slot with start and end
 * @param {Array} existingSlots - Array of existing slots
 * @param {number|null} excludeIndex - Index to exclude (when modifying existing slot)
 * @returns {Object|null} Object with slotIndex and split slots (before/after), or null
 */
export const findSlotToSplit = (
  newSlot,
  existingSlots,
  excludeIndex = null
) => {
  const newStart = timeToMinutes(newSlot.start);
  const newEnd = timeToMinutes(newSlot.end);

  for (let i = 0; i < existingSlots.length; i++) {
    if (i === excludeIndex) continue;

    const slot = existingSlots[i];
    const slotStart = timeToMinutes(slot.start);
    const slotEnd = timeToMinutes(slot.end);

    // New slot is completely inside this slot (needs splitting)
    if (newStart > slotStart && newEnd < slotEnd) {
      // Create before slot: original start -> 1 minute before new slot
      const beforeEnd = minutesToTime(newStart - 1);
      const beforeSlot = { ...slot, end: beforeEnd };
      const beforeValid = validateDuration(slot.start, beforeEnd);

      // Create after slot: 1 minute after new slot -> original end
      const afterStart = minutesToTime(newEnd + 1);
      const afterSlot = { ...slot, start: afterStart };
      const afterValid = validateDuration(afterStart, slot.end);

      return {
        slotIndex: i,
        beforeSlot: beforeValid ? beforeSlot : null,
        afterSlot: afterValid ? afterSlot : null,
      };
    }
  }

  return null;
};

/**
 * Resolve all overlaps caused by a new/modified slot
 * Returns a new array of slots with adjustments and removals applied
 * @param {Object} newSlot - New slot with start and end (and value)
 * @param {Array} existingSlots - Array of existing slots
 * @param {number|null} slotIndex - Index of slot being modified (null for new slot)
 * @returns {Object} Object with resolvedSlots and summary info
 */
export const resolveSlotOverlaps = (
  newSlot,
  existingSlots,
  slotIndex = null
) => {
  // Step 1: Check if new slot splits an existing slot
  const splitResult = findSlotToSplit(newSlot, existingSlots, slotIndex);

  if (splitResult) {
    // Handle split case separately
    const resolvedSlots = [];
    const removedIndices = new Set();

    existingSlots.forEach((slot, index) => {
      if (index === slotIndex) {
        // Skip the slot being modified
        return;
      }

      if (index === splitResult.slotIndex) {
        // Replace with split slots (only valid ones)
        if (splitResult.beforeSlot) {
          resolvedSlots.push(splitResult.beforeSlot);
        }
        if (splitResult.afterSlot) {
          resolvedSlots.push(splitResult.afterSlot);
        }

        // Track if original was removed (both parts invalid)
        if (!splitResult.beforeSlot && !splitResult.afterSlot) {
          removedIndices.add(index);
        }
      } else {
        // Keep other slots as is
        resolvedSlots.push(slot);
      }
    });

    // Add the new slot
    resolvedSlots.push(newSlot);

    // Sort by start time
    resolvedSlots.sort((a, b) => {
      return timeToMinutes(a.start) - timeToMinutes(b.start);
    });

    return {
      resolvedSlots,
      removedCount: removedIndices.size,
      adjustedCount:
        (splitResult.beforeSlot ? 1 : 0) + (splitResult.afterSlot ? 1 : 0),
      splitCount: splitResult.beforeSlot && splitResult.afterSlot ? 1 : 0,
    };
  }

  // Step 2: Find fully covered slots (to remove)
  const fullyCoveredIndices = findFullyCoveredSlots(
    newSlot,
    existingSlots,
    slotIndex
  );

  // Step 3: Find slot covered at start (to adjust end)
  const coveredAtStart = findSlotCoveredAtStart(
    newSlot,
    existingSlots,
    slotIndex
  );

  // Step 4: Find slot covered at end (to adjust start)
  const coveredAtEnd = findSlotCoveredAtEnd(newSlot, existingSlots, slotIndex);

  // Build the new slots array
  const resolvedSlots = [];
  const removedIndices = new Set(fullyCoveredIndices);

  // Add slots that are adjusted or removed due to being too short
  if (coveredAtStart) {
    if (coveredAtStart.adjustedSlot === null) {
      removedIndices.add(coveredAtStart.slotIndex);
    }
  }

  if (coveredAtEnd) {
    if (coveredAtEnd.adjustedSlot === null) {
      removedIndices.add(coveredAtEnd.slotIndex);
    }
  }

  // Build resolved slots array
  existingSlots.forEach((slot, index) => {
    if (index === slotIndex) {
      // Skip the slot being modified (will be replaced by newSlot)
      return;
    }

    if (removedIndices.has(index)) {
      // Skip removed slots
      return;
    }

    // Check if this slot needs adjustment
    if (
      coveredAtStart &&
      coveredAtStart.slotIndex === index &&
      coveredAtStart.adjustedSlot
    ) {
      resolvedSlots.push(coveredAtStart.adjustedSlot);
    } else if (
      coveredAtEnd &&
      coveredAtEnd.slotIndex === index &&
      coveredAtEnd.adjustedSlot
    ) {
      resolvedSlots.push(coveredAtEnd.adjustedSlot);
    } else {
      // Keep slot as is
      resolvedSlots.push(slot);
    }
  });

  // Add the new slot
  if (slotIndex === null) {
    // Creating new slot
    resolvedSlots.push(newSlot);
  } else {
    // Modifying existing slot - replace it
    resolvedSlots.push(newSlot);
  }

  // Sort by start time
  resolvedSlots.sort((a, b) => {
    return timeToMinutes(a.start) - timeToMinutes(b.start);
  });

  return {
    resolvedSlots,
    removedCount: removedIndices.size,
    adjustedCount:
      (coveredAtStart?.adjustedSlot ? 1 : 0) +
      (coveredAtEnd?.adjustedSlot ? 1 : 0),
    splitCount: 0,
  };
};
