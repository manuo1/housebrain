import { useState } from "react";
import TimelineHeader from "./TimelineHeader";
import EquipmentSlotBar from "./EquipmentSlotBar";
import SlotEditModal from "./SlotEditModal";
import { calculateOptimalSlotTimes } from "./utils/slotAutoAdjust";
import { resolveSlotOverlaps } from "./utils/slotOverlapResolver";
import styles from "./Timeline.module.scss";
import { PlanEquipment, Slot } from "../../../models/DailyEquipmentPlan";
import { User } from "../../../contexts/AuthContext";

interface TimelineProps {
  equipments: PlanEquipment[];
  onSlotUpdate: (
    equipmentType: string,
    equipmentId: number | null,
    slotIndex: number | null,
    updatedSlot: Slot | null,
    resolvedSlots?: Slot[]
  ) => void;
  user: User | null;
}

export default function Timeline({ equipments, onSlotUpdate, user }: TimelineProps) {
  const [selectedSlot, setSelectedSlot] = useState<Slot | null>(null);
  const [selectedEquipment, setSelectedEquipment] = useState<PlanEquipment | null>(null);
  const [selectedSlotIndex, setSelectedSlotIndex] = useState<number | null>(null);
  const [isCreating, setIsCreating] = useState<boolean>(false);

  const handleSlotClick = (equipment: PlanEquipment, slotData: Slot, slotIndex: number) => {
    if (!user) return; // Block if not authenticated
    setSelectedEquipment(equipment);
    setSelectedSlot(slotData);
    setSelectedSlotIndex(slotIndex);
    setIsCreating(false);
  };

  const handleEmptyClick = (equipment: PlanEquipment, clickTime: string) => {
    if (!user) return; // Block if not authenticated

    // Calculate optimal times based on adjacent slots
    const { start, end } = calculateOptimalSlotTimes(clickTime, equipment.slots);

    // Determine default value based on existing slots
    let defaultValue = "on"; // Default for programmable equipment
    if (equipment.slots.length > 0) {
      defaultValue = String(equipment.slots[0].value); // Use same type as existing slots
    }

    setSelectedEquipment(equipment);
    setSelectedSlot({ start, end, value: defaultValue });
    setSelectedSlotIndex(null); // null = creation mode
    setIsCreating(true);
  };

  const handleSlotSave = (updatedSlot: Slot) => {
    if (onSlotUpdate && selectedEquipment) {
      // Resolve overlaps with existing slots
      const resolvedSlots = resolveSlotOverlaps(
        updatedSlot,
        selectedEquipment.slots,
        isCreating ? null : selectedSlotIndex
      );

      // Pass the resolved slots to parent
      onSlotUpdate(selectedEquipment.type, selectedEquipment.id, selectedSlotIndex, updatedSlot, resolvedSlots);
    }
    handleCloseModal();
  };

  const handleSlotDelete = () => {
    if (onSlotUpdate && selectedEquipment && selectedSlotIndex !== null) {
      // Pass null to signal deletion
      onSlotUpdate(selectedEquipment.type, selectedEquipment.id, selectedSlotIndex, null);
    }
    handleCloseModal();
  };

  const handleCloseModal = () => {
    setSelectedSlot(null);
    setSelectedEquipment(null);
    setSelectedSlotIndex(null);
    setIsCreating(false);
  };

  if (equipments.length === 0) {
    return (
      <div className={styles.timeline}>
        <div className={styles.empty}>
          <p>Aucun équipement programmable</p>
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

      <div className={styles.equipmentsList}>
        {equipments.map((equipment) => (
          <EquipmentSlotBar
            key={`${equipment.type}-${equipment.id}`}
            equipment={equipment}
            onSlotClick={handleSlotClick}
            onEmptyClick={handleEmptyClick}
          />
        ))}
      </div>

      {selectedSlot && selectedEquipment && (
        <SlotEditModal
          slot={selectedSlot}
          equipmentSlots={selectedEquipment.slots}
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
