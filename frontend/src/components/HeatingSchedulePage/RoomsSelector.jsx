import React from 'react';
import RoomButton from './RoomButton';
import styles from './RoomsSelector.module.scss';

export default function RoomsSelector({
  rooms,
  selectedRoomIds,
  onSelectionChange,
}) {
  if (!rooms || rooms.length === 0) {
    return (
      <div className={styles.empty}>
        <p>Aucune pièce disponible</p>
      </div>
    );
  }

  const allSelected = selectedRoomIds.length === rooms.length;

  const handleToggleAll = () => {
    if (allSelected) {
      onSelectionChange([]);
    } else {
      onSelectionChange(rooms.map((room) => room.id));
    }
  };

  const handleToggleRoom = (roomId) => {
    if (selectedRoomIds.includes(roomId)) {
      onSelectionChange(selectedRoomIds.filter((id) => id !== roomId));
    } else {
      onSelectionChange([...selectedRoomIds, roomId]);
    }
  };

  return (
    <div className={styles.roomsSelector}>
      <h4 className={styles.title}>Pièces</h4>

      {/* Bouton "Toutes les pièces" */}
      <div className={styles.allButtonWrapper}>
        <RoomButton
          isSelected={allSelected}
          isAllButton={true}
          onClick={handleToggleAll}
        />
      </div>

      {/* Liste des pièces */}
      <div className={styles.roomsList}>
        {rooms.map((room) => {
          const isSelected = selectedRoomIds.includes(room.id);
          return (
            <RoomButton
              key={room.id}
              room={room}
              isSelected={isSelected}
              onClick={() => handleToggleRoom(room.id)}
            />
          );
        })}
      </div>
    </div>
  );
}
