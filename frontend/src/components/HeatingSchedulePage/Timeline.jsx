import React, { useState } from 'react';
import TimelineHeader from './TimelineHeader';
import RoomSlotBar from './RoomSlotBar';
import SlotEditModal from './SlotEditModal';
import styles from './Timeline.module.scss';

export default function Timeline({ rooms, selectedRoomIds, onSlotUpdate }) {
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [selectedRoom, setSelectedRoom] = useState(null);
  const [selectedSlotIndex, setSelectedSlotIndex] = useState(null);

  const filteredRooms = rooms.filter((room) =>
    selectedRoomIds.includes(room.id)
  );

  const handleSlotClick = (room, slotData, slotIndex) => {
    setSelectedRoom(room);
    setSelectedSlot(slotData);
    setSelectedSlotIndex(slotIndex);
  };

  const handleSlotSave = (updatedSlot) => {
    if (onSlotUpdate && selectedRoom && selectedSlotIndex !== null) {
      onSlotUpdate(selectedRoom.id, selectedSlotIndex, updatedSlot);
    }
    handleCloseModal();
  };

  const handleSlotDelete = () => {
    if (onSlotUpdate && selectedRoom && selectedSlotIndex !== null) {
      // Pass null to signal deletion
      onSlotUpdate(selectedRoom.id, selectedSlotIndex, null);
    }
    handleCloseModal();
  };

  const handleCloseModal = () => {
    setSelectedSlot(null);
    setSelectedRoom(null);
    setSelectedSlotIndex(null);
  };

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
          <RoomSlotBar
            key={room.id}
            room={room}
            onSlotClick={handleSlotClick}
          />
        ))}
      </div>

      {selectedSlot && selectedRoom && (
        <SlotEditModal
          slot={selectedSlot}
          roomSlots={selectedRoom.slots}
          slotIndex={selectedSlotIndex}
          onSave={handleSlotSave}
          onDelete={handleSlotDelete}
          onClose={handleCloseModal}
        />
      )}
    </div>
  );
}
