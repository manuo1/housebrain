import { timeToMinutes, minutesToTime } from "./slotCalculations";
import { Slot } from "../../../../models/DailyHeatingPlan";

interface AdjacentSlots {
  slotBefore: Slot | null;
  slotAfter: Slot | null;
}

export const findAdjacentSlots = (clickTime: string, slots: Slot[]): AdjacentSlots => {
  const clickMin = timeToMinutes(clickTime);
  let slotBefore: Slot | null = null;
  let slotAfter: Slot | null = null;

  // Sort slots by start time
  const sortedSlots = [...slots].sort((a, b) => timeToMinutes(a.start) - timeToMinutes(b.start));

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

export const calculateOptimalSlotTimes = (clickTime: string, slots: Slot[]): { start: string; end: string } => {
  const clickMin = timeToMinutes(clickTime);
  const { slotBefore, slotAfter } = findAdjacentSlots(clickTime, slots);

  let startMin = clickMin;
  let endMin = clickMin + 60; // Default 1 hour

  // If there's a slot before, start 1 minute after it ends
  if (slotBefore) {
    startMin = timeToMinutes(slotBefore.end) + 1;
  } else {
    // No slot before: start at beginning of day (00:00)
    startMin = 0;
  }

  // If there's a slot after, end 1 minute before it starts
  if (slotAfter) {
    endMin = timeToMinutes(slotAfter.start) - 1;
  } else {
    // No slot after: end at end of day (23:59)
    endMin = 1439;
  }

  return {
    start: minutesToTime(startMin),
    end: minutesToTime(endMin),
  };
};
