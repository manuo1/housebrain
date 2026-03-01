import TotalCard from "./TotalCard";
import styles from "./TotalsCards.module.scss";
import { formatWh, formatEuro } from "../../../utils/format";
import { TotalByLabel } from "../../../models/DailyConsumption";

interface TotalsCardsProps {
  totals: Record<string, TotalByLabel> | null | undefined;
}

export default function TotalsCards({ totals }: TotalsCardsProps) {
  if (!totals || typeof totals !== "object" || Object.keys(totals).length === 0) {
    return (
      <div className={styles.totalsCards}>
        <div className={styles.emptyState}>Aucun total disponible</div>
      </div>
    );
  }

  return (
    <div className={styles.totalsCards}>
      {Object.entries(totals).map(([label, total]) => (
        <TotalCard
          key={label}
          label={label}
          kwh={total?.wh != null ? formatWh(total.wh) : "-"}
          euros={total?.euros != null ? formatEuro(total.euros) : "-"}
        />
      ))}
    </div>
  );
}
