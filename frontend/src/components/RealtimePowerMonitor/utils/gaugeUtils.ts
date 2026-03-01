export function getGaugeColor(percent: number): string {
  if (percent <= 30) return "#2dd4bf";
  if (percent <= 60) return "#facc15";
  return "#fb7185";
}

export function percentToDegrees(percent: number): number {
  return (percent / 100) * 180 - 90;
}

export function percentToArcOffset(percent: number, arcLength: number = 126): number {
  return arcLength - (arcLength * percent) / 100;
}
