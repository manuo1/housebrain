import React from "react";
import DisplayConsumptionBlock from "../components/ConsumptionPage/common/DisplayConsumptionBlock";
import styles from "./Consumption.module.scss";

export default function DailyConsumption() {
  return (
    <div className={styles.dailyConsumption}>
      <div className={styles.graphBlock}>
        <DisplayConsumptionBlock />
      </div>
      <div className={styles.graphBlock}>
        <DisplayConsumptionBlock />
      </div>
    </div>
  );
}
