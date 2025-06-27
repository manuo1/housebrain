import React from "react";
import styles from "./ValueSelector.module.scss";

const VALUE_TYPES = [
  { key: "wh", label: "Consommation (Wh)" },
  { key: "average_watt", label: "Puissance Moyenne (w)" },
  { key: "euros", label: "Coût (€)" },
];

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
