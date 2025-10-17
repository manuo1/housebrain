import React from 'react';
import SignalBars from './SignalBars';
import TemperatureTrend from './TemperatureTrend';
import styles from './TemperatureZone.module.scss';

export default function TemperatureZone({
  temperature,
  trend,
  macAddress,
  signalStrength,
}) {
  return (
    <div className={styles.temperatureZone}>
      <span className={styles.label}>Température</span>
      <div className={styles.signal}>
        <SignalBars strength={signalStrength} />
      </div>
      <div className={styles.tempDisplay}>
        {temperature !== null ? (
          <>
            <span className={styles.tempValue}>{temperature.toFixed(1)}°</span>
            <TemperatureTrend trend={trend} />
          </>
        ) : (
          <span className={styles.noData}>—</span>
        )}
      </div>
      <span className={styles.mac}>{macAddress}</span>
    </div>
  );
}
