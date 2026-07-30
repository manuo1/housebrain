import SignalBars from "./SignalBars";
import TemperatureTrend from "./TemperatureTrend";
import styles from "./TemperatureZone.module.scss";
import { TemperatureTrend as TrendType } from "../../models/Room";

interface TemperatureZoneProps {
  temperature: number | null;
  trend: TrendType;
  macAddress: string | null;
  signalStrength: number | null;
}

export default function TemperatureZone({
  temperature,
  trend,
  macAddress,
  signalStrength,
}: TemperatureZoneProps) {
  const hasSensor = macAddress !== null;

  return (
    <div className={styles.temperatureZone}>
      <span className={styles.label}>Température</span>
      {hasSensor ? (
        <>
          <div className={styles.signal}>
            <SignalBars strength={signalStrength ?? 0} />
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
        </>
      ) : (
        <span className={styles.noSensor}>Aucun capteur</span>
      )}
    </div>
  );
}
