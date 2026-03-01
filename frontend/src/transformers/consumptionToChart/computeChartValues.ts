import computeAreaHeight from "./computeAreaHeight";
import computePointColors from "./computePointColors";
import computeLineHeight from "./computeLineHeight";
import computeTooltip from "./computeTooltip";
import { DailyConsumptionElement } from "../../models/DailyConsumption";
import { DisplayType } from "./computeAxisY";

export interface ChartPoint {
  area_height: number;
  area_color: string;
  line_height: number;
  line_color: string;
  tooltip: { title: string; content: string[] };
}

function computeChartValues(
  data: DailyConsumptionElement[],
  displayType: DisplayType,
  maxValue: number
): ChartPoint[] {
  return data.map((point, index) => {
    const value = point[displayType];
    const area_height = computeAreaHeight(value, maxValue);
    const { area_color, line_color } = computePointColors(point.tarif_period, displayType, value);
    const tooltip = computeTooltip(point);

    const nextPoint = data[index + 1];
    let nextValue: number | null = null;
    if (nextPoint) {
      const v = nextPoint[displayType];
      nextValue = v !== null && v !== undefined ? v : null;
    }

    const nextHeight = nextValue !== null ? computeAreaHeight(nextValue, maxValue) : null;
    const line_height = computeLineHeight(area_height, nextHeight);

    return { area_height, area_color, line_height, line_color, tooltip };
  });
}

export default computeChartValues;
