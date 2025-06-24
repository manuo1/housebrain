import React from "react";
import DailyConsumptionBlock from "../components/DailyConsumptionBlock";
import styles from "./DailyConsumption.module.scss";

export default function DailyConsumption() {
  return (
    <div className={styles.dailyConsumption}>
      <div className={styles.graphBlock}>
        <DailyConsumptionBlock />
      </div>
      <div className={styles.graphBlock}>
        <DailyConsumptionBlock />
      </div>
    </div>
  );
}
