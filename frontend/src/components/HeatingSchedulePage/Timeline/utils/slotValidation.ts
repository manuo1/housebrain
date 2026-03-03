import { timeToMinutes } from "./slotCalculations";
import { getValueType } from "./slotTypes";
import { Slot } from "../../../../models/DailyHeatingPlan";

export const validateTime = (startTime: string, endTime: string): boolean => {
  const startMin = timeToMinutes(startTime);
  const endMin = timeToMinutes(endTime);
  return startMin < endMin;
};

export const validateDuration = (startTime: string, endTime: string): boolean => {
  const startMin = timeToMinutes(startTime);
  const endMin = timeToMinutes(endTime);
  const duration = endMin - startMin;
  return duration >= 30;
};

export const validateValue = (val: string): boolean => {
  if (!val) return false;

  // Check if it's on/off
  if (val === "on" || val === "off") return true;

  // Check if it's a valid number
  const num = parseFloat(val);
  return !isNaN(num) && num >= 0 && num <= 30;
};

// Check type consistency with other slots (exclude current slot)
export const checkTypeConsistency = (
  valueInput: string,
  roomSlots: Slot[],
  slotIndex: number | null
): boolean => {
  const newType = getValueType(valueInput);
  if (!newType) return false;

  for (let i = 0; i < roomSlots.length; i++) {
    if (i === slotIndex) continue; // Skip current slot
    const slotValue = roomSlots[i].value;
    if (slotValue == null) continue; // Skip slots without value
    const otherType = getValueType(String(slotValue));
    if (otherType && otherType !== newType) return false;
  }
  return true;
};

interface SlotErrors {
  time?: string;
  value?: string;
}

// Does NOT check overlap - that's handled by auto-adjustment in parent component
export const validateSlot = (
  startTime: string,
  endTime: string,
  valueInput: string,
  roomSlots: Slot[],
  slotIndex: number | null
): SlotErrors => {
  const errors: SlotErrors = {};

  // Validate start < end
  if (!validateTime(startTime, endTime)) {
    errors.time = "L'heure de début doit être avant l'heure de fin";
  } else if (!validateDuration(startTime, endTime)) {
    // Validate minimum duration (30 min)
    errors.time = "La durée minimum d'un créneau est de 30 minutes";
  }

  // Validate value
  if (!validateValue(valueInput)) {
    errors.value = 'Valeur invalide (température 0-30 ou "on"/"off")';
  } else if (!checkTypeConsistency(valueInput, roomSlots, slotIndex)) {
    const currentType = getValueType(valueInput);
    const expectedType = currentType === "temp" ? "on/off" : "température";
    errors.value = `Tous les créneaux doivent être du même type (${expectedType} attendu)`;
  }

  return errors;
};
