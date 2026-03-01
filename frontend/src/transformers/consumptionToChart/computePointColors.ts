import { TARIF_PERIOD_COLORS, DEFAULT_COLOR } from "./constants";
import { DisplayType } from "./computeAxisY";

interface PointColors {
  area_color: string;
  line_color: string;
}

function computePointColors(
  tarifPeriod: string | null | undefined,
  displayType: DisplayType,
  value: number | null | undefined
): PointColors {
  if (value === null || value === undefined) {
    return { area_color: "transparent", line_color: "transparent" };
  }

  if (!tarifPeriod) {
    return {
      area_color: displayType === "average_watt" ? "transparent" : DEFAULT_COLOR,
      line_color: DEFAULT_COLOR,
    };
  }

  const color = TARIF_PERIOD_COLORS[tarifPeriod] || DEFAULT_COLOR;

  return {
    area_color: displayType === "average_watt" ? "transparent" : color,
    line_color: color,
  };
}

export default computePointColors;
