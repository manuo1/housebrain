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

function transformData(data) {
  console.log(data);
  const minutes = Object.keys(data.values.HCHC || {});
  return minutes.map((minute) => ({
    time: minute,
    HCHC: data.values.HCHC[minute],
    HCHP: data.values.HCHP ? data.values.HCHP[minute] : null,
  }));
}

export default function DailyConsumptionChart({ data }) {
  const chartData = transformData(data);

  return (
    <div className={styles.chartContainer}>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart
          data={chartData}
          margin={{ top: 10, right: 30, bottom: 30, left: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" interval={59} tick={{ fontSize: 12 }} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey="HCHC"
            stroke="#8884d8"
            dot={false}
            isAnimationActive={false}
          />
          {data.values.HCHP && (
            <Line
              type="monotone"
              dataKey="HCHP"
              stroke="#82ca9d"
              dot={false}
              isAnimationActive={false}
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
