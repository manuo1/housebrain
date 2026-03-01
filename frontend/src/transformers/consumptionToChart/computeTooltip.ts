import { formatEuro, formatWh } from "../../utils/format";
import { DailyConsumptionElement } from "../../models/DailyConsumption";

interface Tooltip {
  title: string;
  content: string[];
}

function computeTooltip(point: DailyConsumptionElement): Tooltip {
  const { start_time, end_time, average_watt, wh, euros, tarif_period, interpolated } = point;

  const title = `${start_time} → ${end_time}`;

  const content: string[] = [
    `Puissance moyenne: ${average_watt != null ? `${average_watt} W` : "- W"}`,
    `Consommation: ${wh != null ? formatWh(wh) : "- Wh"}`,
    `Coût: ${euros != null ? formatEuro(euros) : "- €"}`,
    `Période Tarifaire: ${tarif_period ?? "-"}`,
  ];

  if (interpolated) {
    content.push("⚠️ Donnée manquante, valeur interpolée");
  }

  return { title, content };
}

export default computeTooltip;
