import { useState } from "react";
import HeatingZone from "./HeatingZone";
import TemperatureZone from "./TemperatureZone";
import RadiatorBadge from "./RadiatorBadge";
import TemperatureTrend from "./TemperatureTrend";
import styles from "./RoomCard.module.scss";
import Room from "../../models/Room";

interface RoomCardProps {
  room: Room;
}

export default function RoomCard({ room }: RoomCardProps) {
  const [expanded, setExpanded] = useState(false);
  const hasRadiator = room.radiator.id !== null;
  const temperature = room.temperature.measurements.temperature;
  const trend = room.temperature.measurements.trend;

  return (
    <>
      {expanded && (
        <div className={styles.backdrop} onClick={() => setExpanded(false)} />
      )}
      <div
        className={`${styles.roomCard} ${expanded ? styles.expanded : ""}`}
        onClick={() => setExpanded((prev) => !prev)}
      >
        <div className={styles.title}>{room.name}</div>

        <div className={styles.miniRow}>
          <RadiatorBadge radiatorState={room.radiator.state} />
          <div className={styles.tempMini}>
            {temperature !== null ? (
              <>
                <span className={styles.tempValue}>{temperature.toFixed(1)}°</span>
                <TemperatureTrend trend={trend} />
              </>
            ) : (
              <span className={styles.noData}>—</span>
            )}
          </div>
        </div>

        {expanded && (
          <div className={styles.details} onClick={(e) => e.stopPropagation()}>
            <HeatingZone
              heatingModeLabel={hasRadiator ? room.heating.mode : null}
              heatingModeValue={hasRadiator ? room.heating.value : null}
              radiatorState={room.radiator.state}
            />
            <TemperatureZone
              temperature={temperature}
              trend={trend}
              macAddress={room.temperature.mac_short}
              signalStrength={room.temperature.signal_strength}
            />
          </div>
        )}
      </div>
    </>
  );
}
