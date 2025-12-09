import React from 'react';
import TimelineHeader from './TimelineHeader';
import RoomSlotBar from './RoomSlotBar';
import styles from './Timeline.module.scss';

export default function Timeline({ rooms, selectedRoomIds }) {
  const filteredRooms = rooms.filter((room) =>
    selectedRoomIds.includes(room.id)
  );

  if (filteredRooms.length === 0) {
    return (
      <div className={styles.timeline}>
        <div className={styles.empty}>
          <p>Aucune pièce sélectionnée</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.timeline}>
      <TimelineHeader />

      <div className={styles.gridOverlay}>
        {Array.from({ length: 11 }).map((_, i) => (
          <div key={i} className={styles.hourLine} />
        ))}
      </div>

      <div className={styles.roomsList}>
        {filteredRooms.map((room) => (
          <RoomSlotBar key={room.id} room={room} />
        ))}
      </div>
    </div>
  );
}
