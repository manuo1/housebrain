import React from 'react';
import PilotageZone from './PilotageZone';
import TemperatureZone from './TemperatureZone';
import RadiatorZone from './RadiatorZone';
import styles from './RoomCard.module.scss';

export default function RoomCard({ room }) {
  return (
    <div className={styles.roomCard}>
      <div className={styles.title}>{room.name}</div>
      <div className={styles.topZones}>
        <PilotageZone mode={room.heating.mode} value={room.heating.value} />

        {room.temperature.id !== null ? (
          <TemperatureZone
            temperature={room.temperature.measurements.temperature}
            trend={room.temperature.measurements.trend}
            macAddress={room.temperature.mac_short}
            signalStrength={room.temperature.signal_strength}
          />
        ) : (
          <div className={styles.noSensor}>
            <span className={styles.label}>Température</span>
            <div className={styles.noSensorContent}>
              <span className={styles.icon}>🌡️</span>
              <span className={styles.text}>Pas de capteur</span>
            </div>
          </div>
        )}
      </div>
      {room.radiator.id !== null ? (
        <RadiatorZone state={room.radiator.state} />
      ) : (
        <RadiatorZone state={null} />
      )}
    </div>
  );
}
