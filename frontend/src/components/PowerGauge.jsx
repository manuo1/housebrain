import React from "react";
import {
  RadialBarChart,
  RadialBar,
  ResponsiveContainer,
  PolarAngleAxis,
} from "recharts";
import styles from "./PowerGauge.module.scss";

export default function PowerGauge({ maxPower, currentPower }) {
  if (!maxPower || currentPower === undefined) {
    maxPower = 1;
    currentPower = 0;
  }

  const percent = (currentPower / maxPower) * 100;

  let fill = "#4CAF50"; // green
  if (percent > 5) fill = "#7CB342"; // lime green
  if (percent > 15) fill = "#FBC02D"; // yellow
  if (percent > 30) fill = "#FB8C00"; // orange
  if (percent > 50) fill = "#AB47BC"; // purple

  const data = [{ name: "Conso", value: currentPower, fill }];

  return (
    <div className={styles.powerGauge}>
      <ResponsiveContainer width="100%" height="100%">
        <RadialBarChart
          cx="50%"
          cy="50%"
          innerRadius="70%"
          outerRadius="100%"
          barSize={25}
          data={data}
          startAngle={225}
          endAngle={-45}
        >
          <PolarAngleAxis
            type="number"
            domain={[0, maxPower]}
            tickCount={6}
            axisLine={false}
            tickFormatter={(value) => `${value} W`}
            tick={{ fill: "#ddd", fontSize: 11, fontWeight: 600 }}
          />
          <RadialBar minAngle={1} clockWise background dataKey="value" />
        </RadialBarChart>
      </ResponsiveContainer>

      <div className={styles.centerText} style={{ color: fill }}>
        {currentPower} W
      </div>
    </div>
  );
}
