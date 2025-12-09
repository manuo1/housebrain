import React from 'react';
import styles from './SlotBarLabel.module.scss';

export default function SlotBarLabel({ roomName }) {
  return <div className={styles.slotBarLabel}>{roomName}</div>;
}
