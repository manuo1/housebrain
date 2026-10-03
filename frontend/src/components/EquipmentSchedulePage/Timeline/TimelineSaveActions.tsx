import styles from "./TimelineSaveActions.module.scss";

interface TimelineSaveActionsProps {
  onCancel: () => void;
  onSave: () => Promise<void>;
  canUndo: boolean;
  hasChanges: boolean;
  onError?: (message: string | null) => void;
}

export default function TimelineSaveActions({ onCancel, onSave, canUndo, hasChanges, onError }: TimelineSaveActionsProps) {
  const handleCancel = () => {
    if (canUndo) onCancel();
  };

  const handleSave = async () => {
    if (hasChanges) {
      onError?.(null);
      try {
        await onSave();
      } catch (error) {
        console.error("Error saving:", error);
        onError?.((error as Error).message || "Erreur lors de l'enregistrement.");
      }
    }
  };

  return (
    <div className={styles.actions}>
      <button className={styles.btnSecondary} onClick={handleCancel} disabled={!canUndo}>
        Annuler
      </button>
      <button className={styles.btnPrimary} onClick={handleSave} disabled={!hasChanges}>
        Enregistrer
      </button>
    </div>
  );
}
