import { MouseEvent } from "react";
import TimeSlot from "./TimeSlot";
import { calculateSlotPosition, percentToTime } from "./utils/slotCalculations";
import styles from "./SlotBar.module.scss";
import { Slot } from "../../../models/DailyHeatingPlan";

interface SlotBarProps {
  slots: Slot[];
  onSlotClick?: (slotData: Slot, index: number) => void;
  onEmptyClick?: (clickTime: string) => void;
}

export default function SlotBar({ slots, onSlotClick, onEmptyClick }: SlotBarProps) {
  const handleSlotClick = (slotData: Slot, index: number) => {
    if (onSlotClick) onSlotClick(slotData, index);
  };

  const handleBarClick = (e: MouseEvent<HTMLDivElement>) => {
    // Check if click was on the bar itself, not on a slot
    if (e.target instanceof HTMLElement && e.target.className.includes("slotBar") && onEmptyClick) {
      const rect = e.currentTarget.getBoundingClientRect();
      const clickX = e.clientX - rect.left;
      const percentClick = (clickX / rect.width) * 100;
      onEmptyClick(percentToTime(percentClick));
    }
  };

  return (
    <div className={styles.slotBar} onClick={handleBarClick}>
      {slots.map((slot, index) => {
        const { left, width } = calculateSlotPosition(slot);
        return (
          <TimeSlot
            key={index}
            left={left}
            width={width}
            value={slot.value}
            start={slot.start}
            end={slot.end}
            onClick={(slotData) => handleSlotClick(slotData as Slot, index)}
          />
        );
      })}
    </div>
  );
}
