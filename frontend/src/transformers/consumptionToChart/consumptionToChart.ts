import computeAxisX from "./computeAxisX";
import computeAxisY, { DisplayType } from "./computeAxisY";
import computeChartValues, { ChartPoint } from "./computeChartValues";
import DailyIndexes from "../../models/DailyConsumption";

interface ChartData {
  axisY: { labels: string[] };
  axisX: { labels: string[] };
  values: ChartPoint[];
}

function transformDailyConsumptionToChart(
  dailyConsumption: DailyIndexes,
  displayType: DisplayType = "wh"
): ChartData {
  if (!dailyConsumption || !dailyConsumption.data) {
    throw new Error("Invalid DailyConsumption object");
  }

  const { step, data } = dailyConsumption;

  const axisX = { labels: computeAxisX(step) };
  const { labels, max } = computeAxisY(data, displayType);
  const axisY = { labels };
  const values = computeChartValues(data, displayType, max);

  return { axisY, axisX, values };
}

export default transformDailyConsumptionToChart;
