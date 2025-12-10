import React from 'react';
import SlotBarLabel from './SlotBarLabel';
import SlotBar from './SlotBar';
import styles from './RoomSlotBar.module.scss';

export default function RoomSlotBar({ room, onSlotClick }) {
  const handleSlotClick = (slotData, slotIndex) => {
    if (onSlotClick) {
      onSlotClick(room, slotData, slotIndex);
    }
  };

  return (
    <div className={styles.roomSlotBar}>
      <SlotBarLabel roomName={room.name} />
      <SlotBar slots={room.slots} onSlotClick={handleSlotClick} />
    </div>
  );
}
