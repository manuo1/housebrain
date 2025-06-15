import React from "react";
import styles from "./DatePicker.module.scss";

export default function DatePicker({ value, onChange }) {
  const handlePrevDay = () => {
    const prev = new Date(value);
    prev.setDate(prev.getDate() - 1);
    onChange(prev.toISOString().slice(0, 10));
  };

  const handleNextDay = () => {
    const next = new Date(value);
    next.setDate(next.getDate() + 1);
    onChange(next.toISOString().slice(0, 10));
  };

  return (
    <div className={styles.datePicker}>
      <button onClick={handlePrevDay} className={styles.navButton}>
        ◀
      </button>
      <input
        type="date"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={styles.dateInput}
      />
      <button onClick={handleNextDay} className={styles.navButton}>
        ▶
      </button>
    </div>
  );
}
