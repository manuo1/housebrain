import React from 'react';
import styles from './RoomButton.module.scss';

export default function RoomButton({
  room,
  isSelected,
  isAllButton = false,
  onClick,
}) {
  const className = [
    styles.roomButton,
    isAllButton && styles.allButton,
    isSelected && styles.active,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <button className={className} onClick={onClick}>
      <span className={styles.name}>{room?.name || 'Toutes les pièces'}</span>
      {isSelected && <span className={styles.checkmark}>✓</span>}
    </button>
  );
}
