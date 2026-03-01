import { findNiceStep, roundToNiceNumber } from "../../utils/niceNumbers";
import { DailyConsumptionElement } from "../../models/DailyConsumption";

export type DisplayType = "average_watt" | "wh" | "euros";

interface AxisYResult {
  labels: string[];
  max: number;
}

function findMaxValue(data: DailyConsumptionElement[], field: DisplayType): number {
  const values = data
    .map((point) => point[field])
    .filter((val): val is number => val !== null && val !== undefined);

  if (values.length === 0) return 0;
  return Math.max(...values);
}

function computeAxisY(data: DailyConsumptionElement[], displayType: DisplayType): AxisYResult {
  const unitMap: Record<DisplayType, string> = {
    average_watt: " W",
    wh: " Wh",
    euros: " €",
  };

  const unit = unitMap[displayType];
  if (!unit) throw new Error(`Invalid display type: ${displayType}`);

  const rawMax = findMaxValue(data, displayType);
  const roundedMax = roundToNiceNumber(rawMax);
  const step = findNiceStep(roundedMax);
  const max = Math.ceil(roundedMax / step) * step;
  const numSteps = max / step;
  const labels: string[] = [];

  for (let i = 0; i <= numSteps; i++) {
    let value = i * step;
    value = displayType === "euros"
      ? Math.round(value * 100) / 100
      : Math.round(value);
    labels.push(`${value}${unit}`);
  }

  return { labels, max };
}

export default computeAxisY;
