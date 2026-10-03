import { CalendarDay as CalendarDayType } from "../../../models/EquipmentCalendar";
import styles from "./CalendarDay.module.scss";

interface CalendarDayProps {
  day: CalendarDayType;
  isCurrentMonth: boolean;
  isSelected: boolean;
  isToday: boolean;
  onClick: () => void;
}

export default function CalendarDay({ day, isCurrentMonth, isSelected, isToday, onClick }: CalendarDayProps) {
  const className = [
    styles.dayButton,
    !isCurrentMonth && styles.otherMonth,
    isSelected && styles.selected,
    isToday && styles.today,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <button className={className} onClick={onClick}>
      {day.date?.day}
    </button>
  );
}
