import React from "react";
import styles from "./PeriodPicker.module.scss";

export default function PeriodPicker({
  startDate,
  endDate,
  onStartChange,
  onEndChange,
}) {
  return (
    <div className={styles.periodPicker}>
      <label>
        Début :
        <input
          type="date"
          value={startDate}
          onChange={(e) => onStartChange(e.target.value)}
          className={styles.dateInput}
        />
      </label>
      <label>
        Fin :
        <input
          type="date"
          value={endDate}
          onChange={(e) => onEndChange(e.target.value)}
          className={styles.dateInput}
        />
      </label>
    </div>
  );
}
