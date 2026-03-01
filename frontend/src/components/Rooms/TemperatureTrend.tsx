import styles from "./TemperatureTrend.module.scss";
import { TemperatureTrend as TrendType } from "../../models/Room";

const TREND_SYMBOLS: Record<string, string> = {
  up: "↑",
  down: "↓",
  same: "→",
};

interface TemperatureTrendProps {
  trend: TrendType;
}

export default function TemperatureTrend({ trend }: TemperatureTrendProps) {
  const symbol = (trend && TREND_SYMBOLS[trend]) || "-";

  return (
    <span className={`${styles.trend} ${trend ? styles[trend] : ""}`}>
      {symbol}
    </span>
  );
}
