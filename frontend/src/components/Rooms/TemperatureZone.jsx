import React from 'react';
import styles from './TemperatureZone.module.scss';

export default function TemperatureZone({
  temperature,
  trend,
  macAddress,
  signalStrength,
}) {
  const getTrendSymbol = (trend) => {
    switch (trend) {
      case 'up':
        return '↑';
      case 'down':
        return '↓';
      case 'same':
        return '→';
      default:
        return '—';
    }
  };

  const SignalBars = ({ strength }) => {
    return (
      <div className={styles.signalBars}>
        {[1, 2, 3, 4, 5].map((bar) => (
          <div
            key={bar}
            className={`${styles.bar} ${bar <= strength ? styles.active : ''}`}
          />
        ))}
      </div>
    );
  };

  return (
    <div className={styles.temperatureZone}>
      <span className={styles.label}>Température</span>
      <div className={styles.content}>
        <div className={styles.top}>
          <SignalBars strength={signalStrength} />
        </div>
        <div className={styles.middle}>
          {temperature !== null ? (
            <>
              <span className={styles.tempValue}>
                {temperature.toFixed(1)}°C
              </span>
              <span className={styles.trend}>{getTrendSymbol(trend)}</span>
            </>
          ) : (
            <span className={styles.noData}>—</span>
          )}
        </div>
        <div className={styles.bottom}>
          <span className={styles.mac}>{macAddress}</span>
        </div>
      </div>
    </div>
  );
}
