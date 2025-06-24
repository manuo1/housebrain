import React from "react";
import styles from "./CustomTooltip.module.scss";
import { formatEuro, formatWh } from "../utils/format";

export default function CustomTooltip({ active, payload }) {
  if (!active || !payload || payload.length === 0) return null;

  const point = payload[0].payload;

  // utile pour le pas afficher le tooltip sur le point fantôme
  if (!point.time_start) return null;

  return (
    <div className={styles.tooltip}>
      <div className={styles.time}>
        {point.time_start}
        {point.time_end ? ` → ${point.time_end}` : ""}
      </div>

      <div className={styles.row}>
        Puissance moyenne:{" "}
        {point.average_watt != null ? `${point.average_watt} W` : "- W"}
      </div>

      <div className={styles.row}>
        Consommation : {point.wh != null ? formatWh(point.wh) : "- Wh"}
      </div>

      <div className={styles.row}>
        Coût : {point.euros != null ? formatEuro(point.euros) : "- €"}
      </div>

      <div className={styles.row}>
        Période Tarifaire :{" "}
        {point.tarif_period != null ? `${point.tarif_period}` : "-"}
      </div>

      {point.interpolated && (
        <div className={styles.warning}>
          ⚠️ Donnée manquante, valeur interpolée
        </div>
      )}
    </div>
  );
}
