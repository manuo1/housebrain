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

// Les index sont enregistrés côté back toutes les minutes : on rafraîchit donc
// toutes les minutes, calé sur la seconde :05 de chaque minute (9:01:05, 9:02:05...)
// pour laisser un peu de marge après l'enregistrement plutôt que de taper pile dessus.
const REFRESH_INTERVAL_MS = 60_000;
const ALIGN_SECOND = 5;

function msUntilNextAlignedTick(): number {
  const now = new Date();
  let secondsUntil = (ALIGN_SECOND - now.getSeconds() + 60) % 60;
  if (secondsUntil === 0) secondsUntil = 60;
  return secondsUntil * 1000 - now.getMilliseconds();
}

export default function ConsumptionSummary() {
  const [yesterday, setYesterday] = useState<DailyConsumption | null>(null);
  const [today, setToday] = useState<DailyConsumption | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [fetchedAt, setFetchedAt] = useState<Date | null>(null);

  useEffect(() => {
    let isMounted = true;
    let intervalId: number | undefined;

    async function load() {
      const todayDate = getTodayDate();
      const yesterdayDate = addDays(todayDate, -1);

      const [yesterdayResult, todayResult] = await Promise.allSettled([
        fetchDailyConsumption(yesterdayDate, STEP),
        fetchDailyConsumption(todayDate, STEP),
      ]);

      if (!isMounted) return;

      if (yesterdayResult.status === "rejected") {
        console.error("Erreur lors du chargement de la conso d'hier:", yesterdayResult.reason);
      }
      if (todayResult.status === "rejected") {
        console.error("Erreur lors du chargement de la conso d'aujourd'hui:", todayResult.reason);
      }

      setYesterday(yesterdayResult.status === "fulfilled" ? yesterdayResult.value : null);
      setToday(todayResult.status === "fulfilled" ? todayResult.value : null);
      setFetchedAt(new Date());
      setIsLoading(false);
    }

    load();

    const timeoutId = window.setTimeout(() => {
      load();
      intervalId = window.setInterval(load, REFRESH_INTERVAL_MS);
    }, msUntilNextAlignedTick());

    return () => {
      isMounted = false;
      window.clearTimeout(timeoutId);
      if (intervalId) window.clearInterval(intervalId);
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
          Aujourd'hui{fetchedAt && ` à ${fetchedAt.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`}
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
