import styles from "./TimelineSaveActions.module.scss";

interface TimelineSaveActionsProps {
  onCancel: () => void;
  onSave: () => Promise<void>;
  canUndo: boolean;
  hasChanges: boolean;
}

export default function TimelineSaveActions({ onCancel, onSave, canUndo, hasChanges }: TimelineSaveActionsProps) {
  const handleCancel = () => {
    if (canUndo) onCancel();
  };

  const handleSave = async () => {
    if (hasChanges) {
      try {
        await onSave();
      } catch (error) {
        console.error("Error saving:", error);
        // TODO: afficher une erreur à l'utilisateur
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
