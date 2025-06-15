import React, { useEffect, useState } from "react";
import fetchTeleinfoData from "../services/fetchTeleinfoData";
import TeleinfoTable from "../components/TeleinfoTable";
import PowerGauge from "../components/PowerGauge";
import styles from "./LiveTeleinfoPage.module.scss";
import { ampereToWatt } from "../utils/consumptionUtils";
// import mockTeleinfoData from "../mocks/mockTeleinfoData";

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
          setError(err.message || "Failed to fetch teleinfo data");
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

  const intensityMax = data && data.ISOUSC ? Number(data.ISOUSC) : 0;
  const maxPower = ampereToWatt(intensityMax);
  const currentPower = data && data.PAPP ? Number(data.PAPP) : 0;

  return (
    <div className={styles.container}>
      <h1>Live Teleinfo Data</h1>
      {error && <p className={styles.error}>Error: {error}</p>}
      {!data && !error && <p>Loading data...</p>}
      {data && (
        <>
          <TeleinfoTable data={data} />
          <PowerGauge maxPower={maxPower} currentPower={currentPower} />
        </>
      )}
    </div>
  );
}
