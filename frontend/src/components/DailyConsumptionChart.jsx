import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import styles from "./DailyConsumptionChart.module.scss";
import { INDEX_LABELS } from "../constants/teleinfoConstants";

// Couleurs des courbes
const colors = [
  "#00E5FF",
  "#FFC107",
  "#FF4081",
  "#7C4DFF",
  "#69F0AE",
  "#F44336",
  "#FFAB00",
];

// Transforme les données pour Recharts
function transformData(values) {
  const allKeys = Object.keys(values);
  const allTimestamps = Object.keys(values[allKeys[0]] || {});
  return allTimestamps.map((minute) => {
    const entry = { time: minute };
    allKeys.forEach((key) => {
      entry[key] = values[key][minute] ?? null;
    });
    return entry;
  });
}

// Label lisible
function getReadableLabel(key) {
  return INDEX_LABELS[key] ?? key;
}

export default function DailyConsumptionChart({ data }) {
  if (!data?.values) return null;

  const chartData = transformData(data.values);
  const keys = Object.keys(data.values);

  return (
    <div className={styles.chartContainer}>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart
          data={chartData}
          margin={{ top: 10, right: 30, bottom: 30, left: 0 }}
        >
          <CartesianGrid stroke="#444" strokeDasharray="3 3" />
          <XAxis
            dataKey="time"
            interval={59}
            tick={{ fontSize: 12, fill: "#ccc" }}
            axisLine={{ stroke: "#555" }}
            tickLine={{ stroke: "#555" }}
          />
          <YAxis
            tick={{ fontSize: 12, fill: "#ccc" }}
            axisLine={{ stroke: "#555" }}
            tickLine={{ stroke: "#555" }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#222",
              border: "none",
              color: "#fff",
            }}
            itemStyle={{ color: "#fff" }}
            labelStyle={{ color: "#fff" }}
            formatter={(value, key) => [value, getReadableLabel(key)]}
          />
          <Legend
            wrapperStyle={{ color: "#ccc" }}
            formatter={(key) => getReadableLabel(key)}
          />
          {keys.map((key, index) => (
            <Line
              key={key}
              type="monotone"
              dataKey={key}
              stroke={colors[index % colors.length]}
              dot={false}
              strokeWidth={2}
              isAnimationActive={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
