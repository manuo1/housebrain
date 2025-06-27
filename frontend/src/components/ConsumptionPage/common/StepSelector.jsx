import React from "react";
import styles from "./StepSelector.module.scss";
import { STEP_OPTIONS } from "../../../constants/consumptionConstants";

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
