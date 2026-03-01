import GaugeArc from "./GaugeArc/GaugeArc";
import GaugeNeedle from "./GaugeNeedle/GaugeNeedle";
import GaugeCenterText from "./GaugeCenterText/GaugeCenterText";
import GaugeTicks from "./GaugeTicks/GaugeTicks";
import styles from "./PowerGauge.module.scss";

interface PowerGaugeProps {
  maxPower: number;
  currentPower: number;
  percent: number;
}

export default function PowerGauge({ maxPower, currentPower, percent }: PowerGaugeProps) {
  return (
    <div className={styles.gaugeContainer}>
      <svg viewBox="0 -5 100 55" className={styles.svg}>
        <GaugeNeedle percent={percent} />
      </svg>
      <svg viewBox="0 -5 100 55" className={styles.svg}>
        <GaugeArc percent={percent} />
        <GaugeCenterText currentPower={currentPower} percent={percent} />
        <GaugeTicks maxPower={maxPower} />
      </svg>
    </div>
  );
}
