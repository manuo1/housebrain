import React from "react";
import styles from "./TotalCard.module.scss";

export default function TotalCard({ label, wh, euros }) {
  const kwh = wh != null ? (wh / 1000).toFixed(2) : "-";
  const euroText = euros != null ? euros.toFixed(2) : "-";

  return (
    <div className={styles.card}>
      <div className={styles.label}>{label} : </div>
      <div className={styles.kwh}>{kwh} kWh</div>
      <div className={styles.separator}>/</div>
      <div className={styles.euros}>{euroText} €</div>
    </div>
  );
}
