import styles from "./DateSelector.module.scss";
import { addDays } from "../../../utils/dateUtils";

interface DateSelectorProps {
  value: string;
  onChange: (date: string) => void;
}

export default function DateSelector({ value, onChange }: DateSelectorProps) {
  const today = new Date().toISOString().split("T")[0];

  const handlePrevious = () => onChange(addDays(value, -1));

  const handleNext = () => {
    if (value < today) onChange(addDays(value, 1));
  };

  return (
    <div className={styles.dateSelector}>
      <button className={styles.navButton} onClick={handlePrevious}>◄</button>
      <input
        type="date"
        className={styles.datePicker}
        value={value}
        max={today}
        onChange={(e) => onChange(e.target.value)}
      />
      <button className={styles.navButton} onClick={handleNext}>►</button>
    </div>
  );
}
