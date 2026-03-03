import RoomButton from "./RoomButton";
import styles from "./RoomsSelector.module.scss";
import { PlanRoom } from "../../../models/DailyHeatingPlan";

interface RoomsSelectorProps {
  rooms: PlanRoom[];
  selectedRoomIds: (number | null)[];
  onSelectionChange: (ids: (number | null)[]) => void;
}

export default function RoomsSelector({ rooms, selectedRoomIds, onSelectionChange }: RoomsSelectorProps) {
  if (!rooms || rooms.length === 0) {
    return (
      <div className={styles.empty}>
        <p>Aucune pièce disponible</p>
      </div>
    );
  }

  const allSelected = selectedRoomIds.length === rooms.length;

  const handleToggleAll = () => {
    onSelectionChange(allSelected ? [] : rooms.map((room) => room.id));
  };

  const handleToggleRoom = (roomId: number | null) => {
    onSelectionChange(
      selectedRoomIds.includes(roomId)
        ? selectedRoomIds.filter((id) => id !== roomId)
        : [...selectedRoomIds, roomId]
    );
  };

  return (
    <div className={styles.roomsSelector}>
      <h4 className={styles.title}>Pièces</h4>
      <div className={styles.allButtonWrapper}>
        <RoomButton isSelected={allSelected} isAllButton={true} onClick={handleToggleAll} />
      </div>
      <div className={styles.roomsList}>
        {rooms.map((room) => (
          <RoomButton
            key={room.id}
            room={room}
            isSelected={selectedRoomIds.includes(room.id)}
            onClick={() => handleToggleRoom(room.id)}
          />
        ))}
      </div>
    </div>
  );
}
