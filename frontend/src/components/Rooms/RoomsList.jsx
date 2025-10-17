import React, { useState, useEffect } from 'react';
import fetchRoomsData from '../../services/fetchRoomsData';
import RoomCard from './RoomCard';
import styles from './RoomsList.module.scss';

export default function RoomsList() {
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadRooms();
    // Polling toutes les 30s
    const interval = setInterval(loadRooms, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadRooms = async () => {
    try {
      setError(null);
      const data = await fetchRoomsData();
      setRooms(data);
    } catch (err) {
      setError('Erreur lors du chargement des pièces');
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
