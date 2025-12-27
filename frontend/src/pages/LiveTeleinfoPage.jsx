import React, { useEffect, useState } from 'react';
import fetchTeleinfoData from '../services/fetchTeleinfoData';
import TeleinfoTable from '../components/TeleinfoTable/TeleinfoTable';
import styles from './LiveTeleinfoPage.module.scss';

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
      {data && <TeleinfoTable data={data} />}
    </div>
  );
}
