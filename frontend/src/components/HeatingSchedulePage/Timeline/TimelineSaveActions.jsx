import React from 'react';
import styles from './TimelineSaveActions.module.scss';

export default function TimelineSaveActions({
  onCancel,
  onSave,
  canUndo,
  hasChanges,
}) {
  const handleCancel = () => {
    if (canUndo) {
      onCancel();
    }
  };

  const handleSave = async () => {
    if (hasChanges) {
      try {
        await onSave();
      } catch (error) {
        console.error('Error saving:', error);
        // TODO: afficher une erreur à l'utilisateur
      }
    }
  };

  return (
    <div className={styles.actions}>
      <button
        className={styles.btnSecondary}
        onClick={handleCancel}
        disabled={!canUndo}
      >
        Annuler
      </button>
      <button
        className={styles.btnPrimary}
        onClick={handleSave}
        disabled={!hasChanges}
      >
        Enregistrer
      </button>
    </div>
  );
}
