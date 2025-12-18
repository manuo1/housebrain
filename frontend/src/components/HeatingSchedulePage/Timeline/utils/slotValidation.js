import { timeToMinutes } from './slotCalculations';
import { getValueType } from './slotTypes';

/**
 * Validate that start time is before end time
 * @param {string} startTime - Start time (HH:MM)
 * @param {string} endTime - End time (HH:MM)
 * @returns {boolean}
 */
export const validateTime = (startTime, endTime) => {
  const startMin = timeToMinutes(startTime);
  const endMin = timeToMinutes(endTime);
  return startMin < endMin;
};

/**
 * Validate minimum duration (30 minutes)
 * @param {string} startTime - Start time (HH:MM)
 * @param {string} endTime - End time (HH:MM)
 * @returns {boolean}
 */
export const validateDuration = (startTime, endTime) => {
  const startMin = timeToMinutes(startTime);
  const endMin = timeToMinutes(endTime);
  const duration = endMin - startMin;
  return duration >= 30;
};

/**
 * Validate slot value (temperature or on/off)
 * @param {string} val - Slot value
 * @returns {boolean}
 */
export const validateValue = (val) => {
  if (!val) return false;

  // Check if it's on/off
  if (val === 'on' || val === 'off') return true;

  // Check if it's a valid number
  const num = parseFloat(val);
  return !isNaN(num) && num >= 0 && num <= 30;
};

/**
 * Check type consistency with other slots in room
 * @param {string} valueInput - Value to check
 * @param {Array} roomSlots - Array of existing slots
 * @param {number|null} slotIndex - Index of current slot (null for new slot)
 * @returns {boolean}
 */
export const checkTypeConsistency = (valueInput, roomSlots, slotIndex) => {
  const newType = getValueType(valueInput);
  if (!newType) return false;

  // Check type consistency with other slots (exclude current slot)
  for (let i = 0; i < roomSlots.length; i++) {
    if (i === slotIndex) continue; // Skip current slot

    const otherType = getValueType(roomSlots[i].value);
    if (otherType && otherType !== newType) {
      return false;
    }
  }
  return true;
};

/**
 * Validate a slot (time, duration, value, type consistency)
 * Does NOT check overlap - that's handled by auto-adjustment in parent component
 * @param {string} startTime - Start time (HH:MM)
 * @param {string} endTime - End time (HH:MM)
 * @param {string} valueInput - Slot value
 * @param {Array} roomSlots - Array of existing slots
 * @param {number|null} slotIndex - Index of current slot (null for new slot)
 * @returns {Object} Object with validation errors
 */
export const validateSlot = (
  startTime,
  endTime,
  valueInput,
  roomSlots,
  slotIndex
) => {
  const errors = {};

  // Validate start < end
  if (!validateTime(startTime, endTime)) {
    errors.time = "L'heure de début doit être avant l'heure de fin";
  }

  // Validate minimum duration (30 min)
  if (!errors.time && !validateDuration(startTime, endTime)) {
    errors.time = "La durée minimum d'un créneau est de 30 minutes";
  }

  // Validate value
  if (!validateValue(valueInput)) {
    errors.value = 'Valeur invalide (température 0-30 ou "on"/"off")';
  } else if (!checkTypeConsistency(valueInput, roomSlots, slotIndex)) {
    const currentType = getValueType(valueInput);
    const expectedType = currentType === 'temp' ? 'on/off' : 'température';
    errors.value = `Tous les créneaux doivent être du même type (${expectedType} attendu)`;
  }

  return errors;
};
