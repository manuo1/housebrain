import SlotBarLabel from "./SlotBarLabel";
import SlotBar from "./SlotBar";
import styles from "./RoomSlotBar.module.scss";
import { PlanRoom } from "../../../models/DailyHeatingPlan";
import { Slot } from "../../../models/DailyHeatingPlan";

interface RoomSlotBarProps {
  room: PlanRoom;
  onSlotClick?: (room: PlanRoom, slotData: Slot, slotIndex: number) => void;
  onEmptyClick?: (room: PlanRoom, clickTime: string) => void;
}

export default function RoomSlotBar({ room, onSlotClick, onEmptyClick }: RoomSlotBarProps) {
  const handleSlotClick = (slotData: Slot, slotIndex: number) => {
    if (onSlotClick) onSlotClick(room, slotData, slotIndex);
  };

  const handleEmptyClick = (clickTime: string) => {
    if (onEmptyClick) onEmptyClick(room, clickTime);
  };

  return (
    <div className={styles.roomSlotBar}>
      <SlotBarLabel roomName={room.name} />
      <SlotBar slots={room.slots} onSlotClick={handleSlotClick} onEmptyClick={handleEmptyClick} />
    </div>
  );
}
