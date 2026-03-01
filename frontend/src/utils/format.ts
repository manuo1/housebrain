export function formatEuro(value: number | null | undefined): string {
  if (value == null) return "- €";
  return value >= 1
    ? `${value.toFixed(2)} €`
    : `${(value * 100).toFixed(2)} cts`;
}

export function formatWh(wh: number | null | undefined): string {
  if (wh == null) return "- Wh";
  return wh >= 1000 ? `${(wh / 1000).toFixed(2)} kWh` : `${wh} Wh`;
}
