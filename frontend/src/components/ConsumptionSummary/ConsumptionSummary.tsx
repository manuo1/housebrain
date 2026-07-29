import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import fetchDailyConsumption from "../../services/fetchDailyConsumption";
import DailyConsumption from "../../models/DailyConsumption";
import TotalsCards from "../ConsumptionBlock/TotalsCards/TotalsCards";
import { getTodayDate, addDays } from "../../utils/dateUtils";
import styles from "./ConsumptionSummary.module.scss";

// Les totaux (data.totals) sont calculés côté backend à partir des index bruts,
// indépendamment du step demandé pour la série temporelle (data.values) : on
// prend donc le step le plus rapide (60 min) puisqu'on n'utilise ici que les totaux.
const STEP = 60;

export default function ConsumptionSummary() {
  const [yesterday, setYesterday] = useState<DailyConsumption | null>(null);
  const [today, setToday] = useState<DailyConsumption | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    let isMounted = true;

    async function load() {
      const todayDate = getTodayDate();
      const yesterdayDate = addDays(todayDate, -1);

      const [yesterdayResult, todayResult] = await Promise.allSettled([
        fetchDailyConsumption(yesterdayDate, STEP),
        fetchDailyConsumption(todayDate, STEP),
      ]);

      if (!isMounted) return;

      setYesterday(yesterdayResult.status === "fulfilled" ? yesterdayResult.value : null);
      setToday(todayResult.status === "fulfilled" ? todayResult.value : null);
      setIsLoading(false);
    }

    load();

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <Link to="/consumption" className={styles.consumptionSummary}>
      <div className={styles.day}>
        <div className={styles.dayLabel}>Hier</div>
        {isLoading ? (
          <p className={styles.loading}>Chargement...</p>
        ) : (
          <TotalsCards totals={yesterday?.totals} />
        )}
      </div>
      <div className={styles.day}>
        <div className={styles.dayLabel}>
          Aujourd'hui <span className={styles.badge}>en cours</span>
        </div>
        {isLoading ? (
          <p className={styles.loading}>Chargement...</p>
        ) : (
          <TotalsCards totals={today?.totals} />
        )}
      </div>
    </Link>
  );
}
