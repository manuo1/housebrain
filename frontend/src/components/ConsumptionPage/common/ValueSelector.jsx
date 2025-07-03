import React from "react";
import styles from "./ValueSelector.module.scss";
import { VALUE_TYPES } from "../../../constants/consumptionConstants";

export default function ValueSelector({ value, onChange }) {
  return (
    <div className={styles.valueSelector}>
      {VALUE_TYPES.map(({ key, label }) => (
        <button
          key={key}
          className={`${styles.button} ${value === key ? styles.active : ""}`}
          onClick={() => onChange(key)}
        >
          {label}
        </button>
      ))}
    </div>
  );
}
