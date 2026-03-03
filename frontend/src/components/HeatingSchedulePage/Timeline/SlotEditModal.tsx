import { useState, useEffect, FormEvent, ChangeEvent } from "react";
import ConfirmModal from "../../common/ConfirmModal";
import { validateSlot } from "./utils/slotValidation";
import styles from "./SlotEditModal.module.scss";
import { Slot } from "../../../models/DailyHeatingPlan";

interface SlotErrors {
  time?: string;
  value?: string;
}

interface SlotEditModalProps {
  slot: Slot | null;
  roomSlots: Slot[];
  slotIndex: number | null;
  isCreating: boolean;
  onSave: (slot: Slot) => void;
  onDelete?: () => void;
  onClose: () => void;
}

export default function SlotEditModal({ slot, roomSlots, slotIndex, isCreating, onSave, onDelete, onClose }: SlotEditModalProps) {
  const [start, setStart] = useState<string>(slot?.start || "00:00");
  const [end, setEnd] = useState<string>(slot?.end || "00:00");
  const [value, setValue] = useState<string>(slot?.value != null ? String(slot.value) : "");
  const [errors, setErrors] = useState<SlotErrors>({});
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<boolean>(false);

  useEffect(() => {
    if (slot) {
      setStart(slot.start);
      setEnd(slot.end);
      setValue(slot.value != null ? String(slot.value) : "");
    }
  }, [slot]);

  // Validate slot (time, duration, value, type consistency)
  const validate = (startTime: string, endTime: string, valueInput: string): boolean => {
    const newErrors = validateSlot(startTime, endTime, valueInput, roomSlots, slotIndex);
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleStartChange = (e: ChangeEvent<HTMLInputElement>) => {
    const newStart = e.target.value;
    setStart(newStart);
    validate(newStart, end, value);
  };

  const handleEndChange = (e: ChangeEvent<HTMLInputElement>) => {
    const newEnd = e.target.value;
    setEnd(newEnd);
    validate(start, newEnd, value);
  };

  const handleValueChange = (e: ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setValue(newValue);
    validate(start, end, newValue);
  };

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (validate(start, end, value)) {
      onSave({ start, end, value });
    }
  };

  const handleConfirmDelete = () => {
    if (onDelete) onDelete();
  };

  const isValid = Object.keys(errors).length === 0 && start && end && value;

  if (!slot) return null;

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
        <h3>{isCreating ? "Créer un créneau" : "Modifier le créneau"}</h3>

        <form onSubmit={handleSubmit}>
          <div className={styles.formGroup}>
            <label htmlFor="start">Début</label>
            <input
              type="time"
              id="start"
              value={start}
              onChange={handleStartChange}
              required
              className={errors.time ? styles.inputError : ""}
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
              className={errors.time ? styles.inputError : ""}
            />
            {errors.time && <span className={styles.errorMessage}>{errors.time}</span>}
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
              className={errors.value ? styles.inputError : ""}
            />
            {errors.value && <span className={styles.errorMessage}>{errors.value}</span>}
          </div>

          <div className={styles.actions}>
            {!isCreating && (
              <button type="button" className={styles.btnDanger} onClick={() => setShowDeleteConfirm(true)}>
                Supprimer
              </button>
            )}
            <div className={styles.rightActions}>
              <button type="button" className={styles.btnSecondary} onClick={onClose}>
                Annuler
              </button>
              <button type="submit" className={styles.btnPrimary} disabled={!isValid}>
                {isCreating ? "Créer" : "Valider"}
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
