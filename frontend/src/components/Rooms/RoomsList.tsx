import { useState, useEffect } from "react";
import fetchRoomsData from "../../services/fetchRoomsData";
import RoomCard from "./RoomCard";
import styles from "./RoomsList.module.scss";
import Room from "../../models/Room";

export default function RoomsList() {
  const [rooms, setRooms] = useState<Room[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadRooms();
    const interval = setInterval(loadRooms, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadRooms = async () => {
    try {
      setError(null);
      const data = await fetchRoomsData();
      setRooms(data);
    } catch (err) {
      setError("Erreur lors du chargement des pièces");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className={styles.roomsList}>
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.roomsList}>
        <div className={styles.error}>
          <span className={styles.errorIcon}>⚠️</span>
          <p>{error}</p>
          <button onClick={loadRooms} className={styles.retryButton}>
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.roomsList}>
      {rooms.length === 0 ? (
        <p className={styles.noRooms}>Aucune pièce configurée</p>
      ) : (
        rooms.map((room) => <RoomCard key={room.id} room={room} />)
      )}
    </div>
  );
}
