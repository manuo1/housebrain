import React from 'react';
import RoomsList from '../components/Rooms/RoomsList';
import styles from './Home.module.scss';

export default function Home() {
  return (
    <div className={styles.home}>
      <div className={styles.dashboardGrid}>
        <div className={styles.roomsSection}>
          <RoomsList />
        </div>

        <div className={styles.statsSection}>
          <div className={styles.placeholder}>
            <span className={styles.icon}>📊</span>
            <h2>Dashboard consommation</h2>
            <p>🚧 En construction…</p>
          </div>
        </div>
      </div>
    </div>
  );
}
