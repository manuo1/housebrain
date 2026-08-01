import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import fetchDailyConsumption from "../../services/fetchDailyConsumption";
import DailyConsumption from "../../models/DailyConsumption";
import TotalsCards from "../ConsumptionBlock/TotalsCards/TotalsCards";
import { getTodayDate, addDays, formatTime } from "../../utils/dateUtils";
import styles from "./ConsumptionSummary.module.scss";

// Les totaux (data.totals) sont calculés côté backend à partir des index bruts,
// indépendamment du step demandé pour la série temporelle (data.values) : on
// prend donc le step le plus rapide (60 min) puisqu'on n'utilise ici que les totaux.
const STEP = 60;

// TODO: refetch périodique désactivé pour l'instant (fetch une seule fois au
// montage). À revoir : "hier" ne change jamais une fois chargé (inutile de le
// refetcher), seul "aujourd'hui" aurait besoin d'un refresh périodique — voir
// piste retenue : ne refetcher "hier" que si la date "hier" calculée change
// (rollover minuit), et "aujourd'hui" à un rythme à définir.

export default function ConsumptionSummary() {
  const [yesterday, setYesterday] = useState<DailyConsumption | null>(null);
  const [today, setToday] = useState<DailyConsumption | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [fetchedAt, setFetchedAt] = useState<Date | null>(null);

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
          Aujourd'hui{fetchedAt && ` à ${formatTime(fetchedAt)}`}
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
