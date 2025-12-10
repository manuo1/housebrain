import React, { useState, useEffect } from 'react';
import styles from './SlotEditModal.module.scss';

export default function SlotEditModal({
  slot,
  roomSlots,
  slotIndex,
  isCreating,
  onSave,
  onDelete,
  onClose,
}) {
  const [start, setStart] = useState(slot?.start || '00:00');
  const [end, setEnd] = useState(slot?.end || '00:00');
  const [value, setValue] = useState(slot?.value || '');
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (slot) {
      setStart(slot.start);
      setEnd(slot.end);
      setValue(slot.value);
    }
  }, [slot]);

  // Validation helpers
  const timeToMinutes = (timeStr) => {
    const [hours, minutes] = timeStr.split(':').map(Number);
    return hours * 60 + minutes;
  };

  const validateTime = (startTime, endTime) => {
    const startMin = timeToMinutes(startTime);
    const endMin = timeToMinutes(endTime);
    return startMin < endMin;
  };

  const checkOverlap = (startTime, endTime) => {
    const startMin = timeToMinutes(startTime);
    const endMin = timeToMinutes(endTime);

    // Check overlap with other slots (exclude current slot)
    for (let i = 0; i < roomSlots.length; i++) {
      if (i === slotIndex) continue; // Skip current slot

      const otherStart = timeToMinutes(roomSlots[i].start);
      const otherEnd = timeToMinutes(roomSlots[i].end);

      // No contact or overlap allowed
      // Valid cases: end < otherStart OR start > otherEnd
      // Invalid (overlap): NOT (end < otherStart OR start > otherEnd)
      if (!(endMin < otherStart || startMin > otherEnd)) {
        return true;
      }
    }
    return false;
  };

  const validateValue = (val) => {
    if (!val) return false;

    // Check if it's on/off
    if (val === 'on' || val === 'off') return true;

    // Check if it's a valid number
    const num = parseFloat(val);
    return !isNaN(num) && num >= 0 && num <= 50;
  };

  const getValueType = (val) => {
    if (val === 'on' || val === 'off') return 'onoff';
    const num = parseFloat(val);
    if (!isNaN(num)) return 'temp';
    return null;
  };

  const checkTypeConsistency = (valueInput) => {
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

  // Validate all fields
  const validate = (startTime, endTime, valueInput) => {
    const newErrors = {};

    // Validate start < end
    if (!validateTime(startTime, endTime)) {
      newErrors.time = "L'heure de début doit être avant l'heure de fin";
    }

    // Validate minimum duration (30 min)
    const startMin = timeToMinutes(startTime);
    const endMin = timeToMinutes(endTime);
    const duration = endMin - startMin;

    if (!newErrors.time && duration < 30) {
      newErrors.time = "La durée minimum d'un créneau est de 30 minutes";
    }

    // Validate overlap
    if (!newErrors.time && checkOverlap(startTime, endTime)) {
      newErrors.overlap = 'Ce créneau chevauche un autre créneau existant';
    }

    // Validate value
    if (!validateValue(valueInput)) {
      newErrors.value = 'Valeur invalide (température 0-50 ou "on"/"off")';
    } else if (!checkTypeConsistency(valueInput)) {
      const currentType = getValueType(valueInput);
      const expectedType = currentType === 'temp' ? 'on/off' : 'température';
      newErrors.value = `Tous les créneaux doivent être du même type (${expectedType} attendu)`;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // On change handlers with validation
  const handleStartChange = (e) => {
    const newStart = e.target.value;
    setStart(newStart);
    validate(newStart, end, value);
  };

  const handleEndChange = (e) => {
    const newEnd = e.target.value;
    setEnd(newEnd);
    validate(start, newEnd, value);
  };

  const handleValueChange = (e) => {
    const newValue = e.target.value;
    setValue(newValue);
    validate(start, end, newValue);
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (validate(start, end, value)) {
      onSave({ start, end, value });
    }
  };

  const handleCancel = () => {
    onClose();
  };

  const handleDelete = () => {
    if (
      onDelete &&
      window.confirm('Êtes-vous sûr de vouloir supprimer ce créneau ?')
    ) {
      onDelete();
    }
  };

  const isValid = Object.keys(errors).length === 0 && start && end && value;

  if (!slot) return null;

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
        <h3>{isCreating ? 'Créer un créneau' : 'Modifier le créneau'}</h3>

        <form onSubmit={handleSubmit}>
          <div className={styles.formGroup}>
            <label htmlFor="start">Début</label>
            <input
              type="time"
              id="start"
              value={start}
              onChange={handleStartChange}
              required
              className={errors.time || errors.overlap ? styles.inputError : ''}
            />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="end">Fin</label>
            <input
              type="time"
              id="end"
              value={end}
              onChange={handleEndChange}
              required
              className={errors.time || errors.overlap ? styles.inputError : ''}
            />
            {errors.time && (
              <span className={styles.errorMessage}>{errors.time}</span>
            )}
            {errors.overlap && (
              <span className={styles.errorMessage}>{errors.overlap}</span>
            )}
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="value">Valeur (température ou on/off)</label>
            <input
              type="text"
              id="value"
              value={value}
              onChange={handleValueChange}
              placeholder="20.5 ou on/off"
              required
              className={errors.value ? styles.inputError : ''}
            />
            {errors.value && (
              <span className={styles.errorMessage}>{errors.value}</span>
            )}
          </div>

          <div className={styles.actions}>
            {!isCreating && (
              <button
                type="button"
                className={styles.btnDanger}
                onClick={handleDelete}
              >
                Supprimer
              </button>
            )}
            <div className={styles.rightActions}>
              <button
                type="button"
                className={styles.btnSecondary}
                onClick={handleCancel}
              >
                Annuler
              </button>
              <button
                type="submit"
                className={styles.btnPrimary}
                disabled={!isValid}
              >
                {isCreating ? 'Créer' : 'Valider'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
