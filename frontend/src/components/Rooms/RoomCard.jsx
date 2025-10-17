import React from 'react';
import HeatingZone from './HeatingZone';
import TemperatureZone from './TemperatureZone';
import styles from './RoomCard.module.scss';

export default function RoomCard({ room }) {
  const hasRadiator = room.radiator.id !== null;

  return (
    <div className={styles.roomCard}>
      <div className={styles.title}>{room.name}</div>
      <HeatingZone
        heatingModeLabel={hasRadiator ? room.heating.mode : null}
        heatingModeValue={hasRadiator ? room.heating.value : null}
        radiatorState={room.radiator.state}
      />
      <TemperatureZone
        temperature={room.temperature.measurements.temperature}
        trend={room.temperature.measurements.trend}
        macAddress={room.temperature.mac_short}
        signalStrength={room.temperature.signal_strength}
      />
    </div>
  );
}
