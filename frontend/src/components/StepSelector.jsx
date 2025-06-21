import React from "react";
import styles from "./StepSelector.module.scss";

export const STEP_OPTIONS = [
  { value: 1, label: "1 min" },
  { value: 30, label: "30 min" },
  { value: 60, label: "1 h" },
];

export default function StepSelector({ step, onChange }) {
  return (
    <div className={styles.stepSelector}>
      {STEP_OPTIONS.map(({ value, label }) => (
        <button
          key={value}
          className={`${styles.button} ${step === value ? styles.active : ""}`}
          onClick={() => onChange(value)}
        >
          {label}
        </button>
      ))}
    </div>
  );
}
