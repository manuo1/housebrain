import React from 'react';
import SlotBarLabel from './SlotBarLabel';
import SlotBar from './SlotBar';
import styles from './RoomSlotBar.module.scss';

export default function RoomSlotBar({ room }) {
  return (
    <div className={styles.roomSlotBar}>
      <SlotBarLabel roomName={room.name} />
      <SlotBar slots={room.slots} />
    </div>
  );
}
