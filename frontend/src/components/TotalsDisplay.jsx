import React from "react";
import TotalCard from "./TotalCard";
import styles from "./TotalsDisplay.module.scss";

export default function TotalsDisplay({ totals }) {
  if (
    !totals ||
    typeof totals !== "object" ||
    Object.keys(totals).length === 0
  ) {
    return <p className={styles.empty}>Aucun total disponible.</p>;
  }

  return (
    <div className={styles.totalsDisplay}>
      <div className={styles.cardGrid}>
        {Object.entries(totals).map(([label, total]) => (
          <TotalCard
            key={label}
            label={label}
            wh={total?.wh}
            euros={total?.euros}
          />
        ))}
      </div>
    </div>
  );
}
