import React from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import CustomTooltip from "./CustomTooltip";

export default function DailyConsumptionChart({
  data,
  chartType = "line", // "line" ou "area"
  valueKey = "average_watt", // Données à afficher
}) {
  if (!data || data.length === 0) return <p>No data to display</p>;

  const fixedLabels = Array.from(
    { length: 24 },
    (_, i) => i.toString().padStart(2, "0") + ":00"
  );

  // Préparer les données pour Recharts
  const chartData = data.map((item) => ({
    time_start: item.start_time,
    time_end: item.end_time,
    average_watt: item.average_watt,
    wh: item.wh,
    euros: item.euros,
    interpolated: item.interpolated,
    tarif_period: item.tarif_period,
  }));

  // Ajout d'un point fantôme pour la dernière étape
  const last = chartData[chartData.length - 1];
  const extendedData = [
    ...chartData,
    {
      average_watt: last.average_watt,
      wh: last.wh,
      euros: last.euros,
    },
  ];

  const ChartComponent = chartType === "area" ? AreaChart : LineChart;
  const GraphComponent = chartType === "area" ? Area : Line;

  return (
    <ResponsiveContainer width="100%" height={300}>
      <ChartComponent
        data={extendedData}
        margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
      >
        <CartesianGrid stroke="#444" strokeDasharray="3 3" />
        <XAxis
          dataKey="time_start"
          ticks={fixedLabels}
          stroke="#ccc"
          tickFormatter={(tick) => {
            const label = tick.replace(":00", "H");
            return label.replace(/^0+/, "");
          }}
        />
        <YAxis stroke="#ccc" />
        <Tooltip content={<CustomTooltip valueKey={valueKey} />} />
        <GraphComponent
          type="stepAfter"
          dataKey={valueKey}
          stroke="#82ca9d"
          fill={chartType === "area" ? "#82ca9d44" : "none"}
          strokeWidth={2}
          dot={false}
          isAnimationActive={true}
        />
      </ChartComponent>
    </ResponsiveContainer>
  );
}
