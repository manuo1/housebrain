import React from "react";
import {
  RadialBarChart,
  RadialBar,
  ResponsiveContainer,
  PolarAngleAxis,
} from "recharts";

export default function PowerGauge({ maxPower, currentPower }) {
  const safeMax = maxPower || 1;
  const safeCurrent = Math.min(currentPower || 0, safeMax);
  const percent = (safeCurrent / safeMax) * 100;

  let fill = "#00C49F";
  if (percent > 25) fill = "#FF8042";
  if (percent > 50) fill = "#FF4C4C";

  const data = [
    {
      name: "Conso",
      value: safeCurrent,
      fill,
    },
  ];

  return (
    <div style={{ width: "100%", height: 300, textAlign: "center" }}>
      <h3>{currentPower} W</h3>

      <ResponsiveContainer width="100%" height="100%">
        <RadialBarChart
          cx="50%"
          cy="50%"
          innerRadius="60%"
          outerRadius="100%"
          barSize={20}
          data={data}
          startAngle={225}
          endAngle={-45}
        >
          <PolarAngleAxis
            type="number"
            domain={[0, safeMax]}
            tick={true}
            tickCount={6}
            axisLine={false}
          />
          <RadialBar
            minAngle={1}
            clockWise
            background
            dataKey="value"
            cornerRadius={10}
          />
        </RadialBarChart>
      </ResponsiveContainer>
    </div>
  );
}
