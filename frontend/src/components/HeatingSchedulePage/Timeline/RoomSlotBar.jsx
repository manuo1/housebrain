import React from 'react';
import SlotBarLabel from './SlotBarLabel';
import SlotBar from './SlotBar';
import styles from './RoomSlotBar.module.scss';

export default function RoomSlotBar({ room, onSlotClick, onEmptyClick }) {
  const handleSlotClick = (slotData, slotIndex) => {
    if (onSlotClick) {
      onSlotClick(room, slotData, slotIndex);
    }
  };

  const handleEmptyClick = (clickTime) => {
    if (onEmptyClick) {
      onEmptyClick(room, clickTime);
    }
  };

  return (
    <div className={styles.roomSlotBar}>
      <SlotBarLabel roomName={room.name} />
      <SlotBar
        slots={room.slots}
        onSlotClick={handleSlotClick}
        onEmptyClick={handleEmptyClick}
      />
    </div>
  );
}
