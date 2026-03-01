import PowerGauge from "./PowerGauge/PowerGauge";
import PowerHistoryGraph from "./PowerHistoryGraph/PowerHistoryGraph";
import styles from "./RealtimePowerMonitor.module.scss";

interface RealtimePowerMonitorProps {
  maxPower: number | null;
  currentPower: number | undefined;
}

export default function RealtimePowerMonitor({ maxPower, currentPower }: RealtimePowerMonitorProps) {
  const resolvedMax = maxPower ?? 1;
  const resolvedCurrent = currentPower ?? 0;
  const percent = (resolvedCurrent / resolvedMax) * 100;

  return (
    <div className={styles.monitor}>
      <PowerGauge maxPower={resolvedMax} currentPower={resolvedCurrent} percent={percent} />
      <PowerHistoryGraph currentPower={resolvedCurrent} maxPower={resolvedMax} />
    </div>
  );
}
