import { useState, useEffect } from "react";
import fetchEquipmentData from "../../services/fetchEquipmentData";
import EquipmentCard from "./EquipmentCard";
import styles from "./EquipmentList.module.scss";
import Equipment from "../../models/Equipment";

export default function EquipmentList() {
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadEquipment();
    const interval = setInterval(loadEquipment, 10000);
    return () => clearInterval(interval);
  }, []);

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
        equipment.map((item) => <EquipmentCard key={item.id} equipment={item} />)
      )}
    </div>
  );
}
