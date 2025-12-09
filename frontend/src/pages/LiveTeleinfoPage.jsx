import React, { useEffect, useState } from 'react';
import fetchTeleinfoData from '../services/fetchTeleinfoData';
import TeleinfoTable from '../components/LiveTeleinfoPage/TeleinfoTable';
import PowerGauge from '../components/LiveTeleinfoPage/PowerGauge';
import styles from './LiveTeleinfoPage.module.scss';

const DEFAULT_VOLTAGE = 230;

export default function LiveTeleinfoPage() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;

    async function fetchData() {
      try {
        const teleinfoData = await fetchTeleinfoData();
        if (isMounted) {
          setData(teleinfoData);
          setError(null);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message || 'Failed to fetch teleinfo data');
        }
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
    <div className={styles.container}>
      {error && <p className={styles.error}>Error: {error}</p>}
      {!data && !error && <p>Loading data...</p>}
      {data && (
        <>
          <PowerGauge
            maxPower={data.maxPower}
            currentPower={data.currentPower}
          />
          <TeleinfoTable data={data} />
        </>
      )}
    </div>
  );
}
