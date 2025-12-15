import React, { useState } from 'react';
import TimelineHeader from './TimelineHeader';
import RoomSlotBar from './RoomSlotBar';
import SlotEditModal from './SlotEditModal';
import styles from './Timeline.module.scss';

export default function Timeline({
  rooms,
  selectedRoomIds,
  onSlotUpdate,
  user,
}) {
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [selectedRoom, setSelectedRoom] = useState(null);
  const [selectedSlotIndex, setSelectedSlotIndex] = useState(null);
  const [isCreating, setIsCreating] = useState(false);

  const filteredRooms = rooms.filter((room) =>
    selectedRoomIds.includes(room.id)
  );

  const handleSlotClick = (room, slotData, slotIndex) => {
    if (!user) return; // Block if not authenticated

    setSelectedRoom(room);
    setSelectedSlot(slotData);
    setSelectedSlotIndex(slotIndex);
    setIsCreating(false);
  };

  const handleEmptyClick = (room, clickTime) => {
    if (!user) return; // Block if not authenticated

    // Calculate end time (1 hour later by default)
    const [hours, minutes] = clickTime.split(':').map(Number);
    const endMinutes = (hours * 60 + minutes + 60) % 1440; // +1h, wrap at 24h
    const endHours = Math.floor(endMinutes / 60);
    const endMins = endMinutes % 60;
    const endTime = `${String(endHours).padStart(2, '0')}:${String(
      endMins
    ).padStart(2, '0')}`;

    // Determine default value based on existing slots
    let defaultValue = '20'; // Default temp
    if (room.slots.length > 0) {
      defaultValue = room.slots[0].value; // Use same type as existing slots
    }

    setSelectedRoom(room);
    setSelectedSlot({ start: clickTime, end: endTime, value: defaultValue });
    setSelectedSlotIndex(null); // null = creation mode
    setIsCreating(true);
  };

  const handleSlotSave = (updatedSlot) => {
    if (onSlotUpdate && selectedRoom) {
      if (isCreating) {
        // Add new slot
        onSlotUpdate(selectedRoom.id, -1, updatedSlot); // -1 = create
      } else if (selectedSlotIndex !== null) {
        // Update existing slot
        onSlotUpdate(selectedRoom.id, selectedSlotIndex, updatedSlot);
      }
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
    setIsCreating(false);
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
            onEmptyClick={handleEmptyClick}
          />
        ))}
      </div>

      {selectedSlot && selectedRoom && (
        <SlotEditModal
          slot={selectedSlot}
          roomSlots={selectedRoom.slots}
          slotIndex={selectedSlotIndex}
          isCreating={isCreating}
          onSave={handleSlotSave}
          onDelete={handleSlotDelete}
          onClose={handleCloseModal}
        />
      )}
    </div>
  );
}
