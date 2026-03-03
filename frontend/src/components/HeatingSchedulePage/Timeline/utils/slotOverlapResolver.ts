import { timeToMinutes, minutesToTime } from "./slotCalculations";
import { validateDuration } from "./slotValidation";
import { Slot } from "../../../../models/DailyHeatingPlan";

interface AdjustResult {
  slotIndex: number;
  adjustedSlot: Slot | null;
}

interface SplitResult {
  slotIndex: number;
  beforeSlot: Slot | null;
  afterSlot: Slot | null;
}

interface OverlapResult {
  resolvedSlots: Slot[];
  removedCount: number;
  adjustedCount: number;
  splitCount: number;
}

export const findFullyCoveredSlots = (
  newSlot: Slot,
  existingSlots: Slot[],
  excludeIndex: number | null = null
): number[] => {
  const newStart = timeToMinutes(newSlot.start);
  const newEnd = timeToMinutes(newSlot.end);
  const coveredIndices: number[] = [];

  existingSlots.forEach((slot, index) => {
    if (index === excludeIndex) return;
    const slotStart = timeToMinutes(slot.start);
    const slotEnd = timeToMinutes(slot.end);

    // Slot is fully covered if new slot starts before/at and ends after/at
    if (newStart <= slotStart && newEnd >= slotEnd) coveredIndices.push(index);
  });

  return coveredIndices;
};

export const findSlotCoveredAtStart = (
  newSlot: Slot,
  existingSlots: Slot[],
  excludeIndex: number | null = null
): AdjustResult | null => {
  const newStart = timeToMinutes(newSlot.start);
  const newEnd = timeToMinutes(newSlot.end);

  for (let i = 0; i < existingSlots.length; i++) {
    if (i === excludeIndex) continue;
    const slot = existingSlots[i];
    const slotStart = timeToMinutes(slot.start);
    const slotEnd = timeToMinutes(slot.end);

    // New slot starts inside this slot and ends after it
    if (newStart > slotStart && newStart < slotEnd && newEnd >= slotEnd) {
      const adjustedEnd = minutesToTime(newStart - 1);

      // Check if adjusted slot is still valid (>= 30 min)
      if (!validateDuration(slot.start, adjustedEnd)) {
        // Slot would be too short, mark for removal
        return { slotIndex: i, adjustedSlot: null };
      }
      return { slotIndex: i, adjustedSlot: { ...slot, end: adjustedEnd } };
    }
  }
  return null;
};

export const findSlotCoveredAtEnd = (
  newSlot: Slot,
  existingSlots: Slot[],
  excludeIndex: number | null = null
): AdjustResult | null => {
  const newStart = timeToMinutes(newSlot.start);
  const newEnd = timeToMinutes(newSlot.end);

  for (let i = 0; i < existingSlots.length; i++) {
    if (i === excludeIndex) continue;
    const slot = existingSlots[i];
    const slotStart = timeToMinutes(slot.start);
    const slotEnd = timeToMinutes(slot.end);

    // New slot starts before this slot and ends inside it
    if (newStart <= slotStart && newEnd >= slotStart && newEnd < slotEnd) {
      const adjustedStart = minutesToTime(newEnd + 1);

      // Check if adjusted slot is still valid (>= 30 min)
      if (!validateDuration(adjustedStart, slot.end)) {
        // Slot would be too short, mark for removal
        return { slotIndex: i, adjustedSlot: null };
      }
      return { slotIndex: i, adjustedSlot: { ...slot, start: adjustedStart } };
    }
  }
  return null;
};

export const findSlotToSplit = (
  newSlot: Slot,
  existingSlots: Slot[],
  excludeIndex: number | null = null
): SplitResult | null => {
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

export const resolveSlotOverlaps = (
  newSlot: Slot,
  existingSlots: Slot[],
  slotIndex: number | null = null
): OverlapResult => {
  // Step 1: Check if new slot splits an existing slot
  const splitResult = findSlotToSplit(newSlot, existingSlots, slotIndex);

  if (splitResult) {
    const resolvedSlots: Slot[] = [];
    const removedIndices = new Set<number>();

    existingSlots.forEach((slot, index) => {
      if (index === slotIndex) return; // Skip the slot being modified

      if (index === splitResult.slotIndex) {
        // Replace with split slots (only valid ones)
        if (splitResult.beforeSlot) resolvedSlots.push(splitResult.beforeSlot);
        if (splitResult.afterSlot) resolvedSlots.push(splitResult.afterSlot);

        // Track if original was removed (both parts invalid)
        if (!splitResult.beforeSlot && !splitResult.afterSlot) removedIndices.add(index);
      } else {
        // Keep other slots as is
        resolvedSlots.push(slot);
      }
    });

    resolvedSlots.push(newSlot);
    resolvedSlots.sort((a, b) => timeToMinutes(a.start) - timeToMinutes(b.start));

    return {
      resolvedSlots,
      removedCount: removedIndices.size,
      adjustedCount: (splitResult.beforeSlot ? 1 : 0) + (splitResult.afterSlot ? 1 : 0),
      splitCount: splitResult.beforeSlot && splitResult.afterSlot ? 1 : 0,
    };
  }

  // Step 2: Find fully covered slots (to remove)
  const fullyCoveredIndices = findFullyCoveredSlots(newSlot, existingSlots, slotIndex);

  // Step 3: Find slot covered at start (to adjust end)
  const coveredAtStart = findSlotCoveredAtStart(newSlot, existingSlots, slotIndex);

  // Step 4: Find slot covered at end (to adjust start)
  const coveredAtEnd = findSlotCoveredAtEnd(newSlot, existingSlots, slotIndex);

  const resolvedSlots: Slot[] = [];
  const removedIndices = new Set<number>(fullyCoveredIndices);

  if (coveredAtStart?.adjustedSlot === null) removedIndices.add(coveredAtStart.slotIndex);
  if (coveredAtEnd?.adjustedSlot === null) removedIndices.add(coveredAtEnd.slotIndex);

  existingSlots.forEach((slot, index) => {
    if (index === slotIndex) return; // Skip the slot being modified (will be replaced by newSlot)
    if (removedIndices.has(index)) return; // Skip removed slots

    // Check if this slot needs adjustment
    if (coveredAtStart?.slotIndex === index && coveredAtStart.adjustedSlot) {
      resolvedSlots.push(coveredAtStart.adjustedSlot);
    } else if (coveredAtEnd?.slotIndex === index && coveredAtEnd.adjustedSlot) {
      resolvedSlots.push(coveredAtEnd.adjustedSlot);
    } else {
      // Keep slot as is
      resolvedSlots.push(slot);
    }
  });

  // Add the new slot
  resolvedSlots.push(newSlot);
  resolvedSlots.sort((a, b) => timeToMinutes(a.start) - timeToMinutes(b.start));

  return {
    resolvedSlots,
    removedCount: removedIndices.size,
    adjustedCount: (coveredAtStart?.adjustedSlot ? 1 : 0) + (coveredAtEnd?.adjustedSlot ? 1 : 0),
    splitCount: 0,
  };
};
