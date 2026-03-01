import styles from "./HeatingControl.module.scss";
import { HeatingMode } from "../../models/Room";

const MODE_LABELS: Record<string, string> = {
  thermostat: "Thermostat",
  on_off: "On/Off",
};

const VALUE_LABELS: Record<string, string> = {
  on: "On",
  off: "Off",
  unknown: "Inconnu",
};

interface HeatingControlProps {
  heatingModeValue: string | number | null;
  heatingModeLabel: HeatingMode | null;
}

export default function HeatingControl({ heatingModeValue, heatingModeLabel }: HeatingControlProps) {
  if (heatingModeValue === null && heatingModeLabel === null) {
    return <div className={styles.heatingModeValue}>-</div>;
  }

  const displayLabel = heatingModeLabel ? (MODE_LABELS[heatingModeLabel] || heatingModeLabel) : "-";
  const displayValue = heatingModeValue !== null
    ? (VALUE_LABELS[String(heatingModeValue)] || `${heatingModeValue}°`)
    : "-";

  return (
    <div className={styles.heatingModeValue}>
      {displayLabel} : {displayValue}
    </div>
  );
}
