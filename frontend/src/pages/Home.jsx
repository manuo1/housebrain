import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import RoomsList from '../components/Rooms/RoomsList';
import RealtimePowerMonitor from '../components/RealtimePowerMonitor/RealtimePowerMonitor';
import fetchTeleinfoData from '../services/fetchTeleinfoData';
import styles from './Home.module.scss';

export default function Home() {
  const [teleinfoData, setTeleinfoData] = useState(null);

  useEffect(() => {
    let isMounted = true;

    async function fetchData() {
      try {
        const data = await fetchTeleinfoData();
        if (isMounted) {
          setTeleinfoData(data);
        }
      } catch (err) {
        console.error('Failed to fetch teleinfo data:', err);
      }
    }

    fetchData();
    const interval = setInterval(fetchData, 1000);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <div className={styles.home}>
      <div className={styles.dashboardGrid}>
        <div className={styles.roomsSection}>
          <RoomsList />
        </div>
        <div className={styles.statsSection}>
          {teleinfoData && (
            <div className={styles.powerCard}>
              <div className={styles.tariffBadge}>
                <span className={styles.tariffLabel}>Période tarifaire :</span>
                <span className={styles.tariffValue}>
                  {teleinfoData.PTECLabel || 'N/A'}
                </span>
              </div>

              <RealtimePowerMonitor
                maxPower={teleinfoData.maxPower}
                currentPower={teleinfoData.currentPower}
              />
            </div>
          )}

          <div className={styles.constructionCard}>
            <p className={styles.infoText}>
              Récapitulatif de consommation en cours de construction.
            </p>
            <Link to="/consumption" className={styles.link}>
              <span className={styles.linkIcon}>📈</span>
              Consulter l'historique de consommation
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
