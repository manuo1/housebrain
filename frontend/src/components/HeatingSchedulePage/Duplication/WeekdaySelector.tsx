import { getDayShort } from "../../../utils/dateUtils";
import styles from "./WeekdaySelector.module.scss";

const WEEKDAYS: { key: string; isoWeekday: number }[] = [
  { key: "monday",    isoWeekday: 1 },
  { key: "tuesday",   isoWeekday: 2 },
  { key: "wednesday", isoWeekday: 3 },
  { key: "thursday",  isoWeekday: 4 },
  { key: "friday",    isoWeekday: 5 },
  { key: "saturday",  isoWeekday: 6 },
  { key: "sunday",    isoWeekday: 7 },
];

interface WeekdaySelectorProps {
  selectedDays: string[];
  onChange: (days: string[]) => void;
}

export default function WeekdaySelector({ selectedDays, onChange }: WeekdaySelectorProps) {
  const toggleDay = (day: string) => {
    onChange(
      selectedDays.includes(day)
        ? selectedDays.filter((d) => d !== day)
        : [...selectedDays, day]
    );
  };

  return (
    <div className={styles.weekdaySelector}>
      <label>Répéter les</label>
      <div className={styles.days}>
        {WEEKDAYS.map((day) => (
          <button
            key={day.key}
            className={selectedDays.includes(day.key) ? styles.active : ""}
            onClick={() => toggleDay(day.key)}
          >
            {getDayShort(day.isoWeekday)}
          </button>
        ))}
      </div>
    </div>
  );
}
