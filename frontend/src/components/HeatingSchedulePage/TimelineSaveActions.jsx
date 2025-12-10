import React from 'react';
import styles from './TimelineSaveActions.module.scss';

export default function TimelineSaveActions() {
  const handleCancel = () => {
    // TODO: undo changes
  };

  const handleSave = () => {
    // TODO: POST to backend
  };

  return (
    <div className={styles.actions}>
      <button className={styles.btnSecondary} onClick={handleCancel}>
        Annuler
      </button>
      <button className={styles.btnPrimary} onClick={handleSave}>
        Enregistrer
      </button>
    </div>
  );
}
