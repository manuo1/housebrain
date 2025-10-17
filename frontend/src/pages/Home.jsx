import React from 'react';
import RoomsPanel from '../components/Rooms/RoomsPanel';
import styles from './Home.module.scss';

export default function Home() {
  return (
    <div className={styles.home}>
      <div className={styles.dashboardGrid}>
        <div className={styles.roomsSection}>
          <RoomsPanel />
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
