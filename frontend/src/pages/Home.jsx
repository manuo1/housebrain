import React from 'react';
import { Link } from 'react-router-dom';
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
            <h2>Dashboard</h2>
            <p className={styles.constructionText}>En construction…</p>
            <div className={styles.linksContainer}>
              <p className={styles.infoText}>
                En attendant, vous pouvez consulter :
              </p>
              <div className={styles.links}>
                <Link to="/teleinfo" className={styles.link}>
                  <span className={styles.linkIcon}>⚡</span>
                  Téléinformation
                </Link>
                <Link to="/consumption" className={styles.link}>
                  <span className={styles.linkIcon}>📈</span>
                  Historique de consommation
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
