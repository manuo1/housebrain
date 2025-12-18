import React, { useState, useEffect } from 'react';
import ConfirmModal from '../../common/ConfirmModal/';
import { validateSlot } from './utils/slotValidation';
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
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  useEffect(() => {
    if (slot) {
      setStart(slot.start);
      setEnd(slot.end);
      setValue(slot.value);
    }
  }, [slot]);

  // Validate all fields
  const validate = (startTime, endTime, valueInput) => {
    const newErrors = validateSlot(
      startTime,
      endTime,
      valueInput,
      roomSlots,
      slotIndex
    );
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
    setShowDeleteConfirm(true);
  };

  const handleConfirmDelete = () => {
    if (onDelete) {
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

        <ConfirmModal
          isOpen={showDeleteConfirm}
          onClose={() => setShowDeleteConfirm(false)}
          onConfirm={handleConfirmDelete}
          title="Supprimer le créneau"
          message="Êtes-vous sûr de vouloir supprimer ce créneau ?"
          confirmText="Supprimer"
          cancelText="Annuler"
          confirmVariant="danger"
        />
      </div>
    </div>
  );
}
