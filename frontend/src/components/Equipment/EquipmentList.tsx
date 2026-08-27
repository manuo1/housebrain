import { useState, useEffect, useRef } from "react";
import fetchEquipmentData from "../../services/fetchEquipmentData";
import EquipmentCard from "./EquipmentCard";
import styles from "./EquipmentList.module.scss";
import Equipment from "../../models/Equipment";

const NORMAL_POLL_MS = 10000;
const FAST_POLL_MS = 500;
const FAST_POLL_DURATION_MS = 5000;

export default function EquipmentList() {
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const revertTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const delayRef = useRef<number>(NORMAL_POLL_MS);

  useEffect(() => {
    scheduleNext(0);
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      if (revertTimeoutRef.current) clearTimeout(revertTimeoutRef.current);
    };
  }, []);

  const scheduleNext = (delay: number) => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(async () => {
      await loadEquipment();
      scheduleNext(delayRef.current);
    }, delay);
  };

  // Déclenché après un trigger d'ouverture de porte de garage : polling accéléré
  // temporaire pour un retour visuel rapide, puis retour au polling normal.
  const triggerFastPoll = () => {
    delayRef.current = FAST_POLL_MS;
    scheduleNext(0);
    if (revertTimeoutRef.current) clearTimeout(revertTimeoutRef.current);
    revertTimeoutRef.current = setTimeout(() => {
      delayRef.current = NORMAL_POLL_MS;
    }, FAST_POLL_DURATION_MS);
  };

  const loadEquipment = async () => {
    try {
      setError(null);
      const data = await fetchEquipmentData();
      setEquipment(data);
    } catch (err) {
      setError("Erreur lors du chargement des équipements");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className={styles.equipmentList}>
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.equipmentList}>
        <div className={styles.error}>
          <span className={styles.errorIcon}>⚠️</span>
          <p>{error}</p>
          <button onClick={loadEquipment} className={styles.retryButton}>
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.equipmentList}>
      {equipment.length === 0 ? (
        <p className={styles.noEquipment}>Aucun équipement configuré</p>
      ) : (
        equipment.map((item) => (
          <EquipmentCard key={item.id} equipment={item} onOpeningTriggered={triggerFastPoll} />
        ))
      )}
    </div>
  );
}
