import React from "react";
import styles from "./TeleinfoTable.module.scss";

import { formatLocalDate } from "../utils/dateUtils";

export default function TeleinfoTable({ data }) {
  if (!data) return <p>No data</p>;

  return (
    <table className={styles.table}>
      <thead>
        <tr>
          <th>Label</th>
          <th>Value</th>
        </tr>
      </thead>
      <tbody>
        {Object.entries(data).map(([key, val]) => {
          const displayValue = key === "last_read" ? formatLocalDate(val) : val;

          return (
            <tr key={key}>
              <td>{key}</td>
              <td>{displayValue}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
