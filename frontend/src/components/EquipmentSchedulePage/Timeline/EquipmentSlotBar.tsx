import SlotBarLabel from "./SlotBarLabel";
import SlotBar from "./SlotBar";
import styles from "./EquipmentSlotBar.module.scss";
import { PlanEquipment, Slot } from "../../../models/DailyEquipmentPlan";

interface EquipmentSlotBarProps {
  equipment: PlanEquipment;
  onSlotClick?: (equipment: PlanEquipment, slotData: Slot, slotIndex: number) => void;
  onEmptyClick?: (equipment: PlanEquipment, clickTime: string) => void;
}

export default function EquipmentSlotBar({ equipment, onSlotClick, onEmptyClick }: EquipmentSlotBarProps) {
  const handleSlotClick = (slotData: Slot, slotIndex: number) => {
    if (onSlotClick) onSlotClick(equipment, slotData, slotIndex);
  };

  const handleEmptyClick = (clickTime: string) => {
    if (onEmptyClick) onEmptyClick(equipment, clickTime);
  };

  return (
    <div className={styles.equipmentSlotBar}>
      <SlotBarLabel equipmentName={equipment.name} />
      <SlotBar slots={equipment.slots} onSlotClick={handleSlotClick} onEmptyClick={handleEmptyClick} />
    </div>
  );
}
