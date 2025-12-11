import React from 'react';
import styles from './DuplicationApplyButton.module.scss';

export default function DuplicationApplyButton({ onClick, disabled }) {
  return (
    <button
      className={styles.applyButton}
      onClick={onClick}
      disabled={disabled}
    >
      Appliquer la duplication
    </button>
  );
}
