import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import fetchDailyConsumption from "../../services/fetchDailyConsumption";
import DailyConsumption from "../../models/DailyConsumption";
import TotalsCards from "../ConsumptionBlock/TotalsCards/TotalsCards";
import { getTodayDate, addDays, formatTime, formatDateDD_MM_YYYY } from "../../utils/dateUtils";
import styles from "./ConsumptionSummary.module.scss";

// Les totaux (data.totals) sont calculés côté backend à partir des index bruts,
// indépendamment du step demandé pour la série temporelle (data.values) : on
// prend donc le step le plus rapide (60 min) puisqu'on n'utilise ici que les totaux.
const STEP = 60;

// Rythme de refresh d'"aujourd'hui" : une fois par minute, décalé de quelques
// secondes après le passage de la minute pour laisser le temps aux données
// teleinfo de la minute écoulée d'être disponibles côté backend.
const TICK_OFFSET_SECONDS = 5;

export default function ConsumptionSummary() {
  const [yesterday, setYesterday] = useState<DailyConsumption | null>(null);
  const [today, setToday] = useState<DailyConsumption | null>(null);
  const [yesterdayDate, setYesterdayDate] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [fetchedAt, setFetchedAt] = useState<Date | null>(null);

  // Date "aujourd'hui" actuellement chargée, utilisée pour détecter le
  // rollover de minuit entre deux ticks, sans dépendance de useEffect.
  const loadedTodayDateRef = useRef<string>("");

  useEffect(() => {
    let isMounted = true;
    let timeoutId: ReturnType<typeof setTimeout>;

    async function fetchAndApply(dayChanged: boolean) {
      const todayDate = getTodayDate();
      const newYesterdayDate = addDays(todayDate, -1);

      const [todayResult, yesterdayResult] = await Promise.allSettled([
        fetchDailyConsumption(todayDate, STEP),
        dayChanged ? fetchDailyConsumption(newYesterdayDate, STEP) : Promise.resolve(null),
      ]);

      if (!isMounted) return;

      if (todayResult.status === "rejected") {
        console.error("Erreur lors du chargement de la conso d'aujourd'hui:", todayResult.reason);
      } else {
        setToday(todayResult.value);
      }

      if (dayChanged) {
        if (yesterdayResult.status === "rejected") {
          console.error("Erreur lors du chargement de la conso d'hier:", yesterdayResult.reason);
        } else if (yesterdayResult.value !== null) {
          setYesterday(yesterdayResult.value);
        }
        setYesterdayDate(newYesterdayDate);
      }

      loadedTodayDateRef.current = todayDate;
      setFetchedAt(new Date());
      setIsLoading(false);
    }

    function msUntilNextTick(): number {
      const now = new Date();
      let secondsUntilTarget = TICK_OFFSET_SECONDS - now.getSeconds();
      if (secondsUntilTarget <= 0) secondsUntilTarget += 60;
      return secondsUntilTarget * 1000 - now.getMilliseconds();
    }

    function scheduleNextTick() {
      timeoutId = setTimeout(tick, msUntilNextTick());
    }

    async function tick() {
      const dayChanged = getTodayDate() !== loadedTodayDateRef.current;
      await fetchAndApply(dayChanged);
      if (isMounted) scheduleNextTick();
    }

    // Chargement initial : toujours les deux jours.
    fetchAndApply(true);
    scheduleNextTick();

    return () => {
      isMounted = false;
      clearTimeout(timeoutId);
    };
  }, []);

  return (
    <Link to="/consumption" className={styles.consumptionSummary}>
      <div className={styles.day}>
        <div className={styles.dayLabel}>
          Hier{yesterdayDate && ` ${formatDateDD_MM_YYYY(yesterdayDate)}`}
        </div>
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
