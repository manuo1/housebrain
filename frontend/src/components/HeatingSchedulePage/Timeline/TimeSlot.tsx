import { getSlotClass, getLabel } from "./utils/slotTypes";
import styles from "./TimeSlot.module.scss";
import { Slot } from "../../../models/DailyHeatingPlan";

interface TimeSlotProps {
  left: string;
  width: string;
  value: Slot["value"];
  start: string;
  end: string;
  onClick: (slotData: { start: string; end: string; value: Slot["value"] }) => void;
}

export default function TimeSlot({ left, width, value, start, end, onClick }: TimeSlotProps) {
  const strValue = value != null ? String(value) : "";
  const className = [styles.slot, getSlotClass(strValue, styles)].filter(Boolean).join(" ");

  const handleClick = () => {
    onClick({ start, end, value });
  };

  return (
    <div className={className} style={{ left, width }} title={`${start} - ${end}`} onClick={handleClick}>
      {getLabel(strValue)}
    </div>
  );
}
