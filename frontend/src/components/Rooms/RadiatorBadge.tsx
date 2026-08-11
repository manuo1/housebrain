import styles from "./RadiatorBadge.module.scss";
import RadiatorIcon from "./RadiatorIcon";
import { RadiatorState as RadiatorStateType } from "../../models/Room";

type BadgeColor = "gray" | "red" | "blue" | "yellow";

interface ColorInfo {
  color: BadgeColor;
  pulse: boolean;
  label: string;
}

const getColorInfo = (state: RadiatorStateType | null): ColorInfo => {
  switch (state) {
    case "on":
      return { color: "red", pulse: false, label: "Allumé" };
    case "off":
      return { color: "blue", pulse: false, label: "Éteint" };
    case "load_shed":
      return { color: "yellow", pulse: false, label: "Délestage" };
    case "turning_on":
      return { color: "red", pulse: true, label: "Allumage" };
    case "shutting_down":
      return { color: "blue", pulse: true, label: "Arrêt" };
    default:
      return { color: "gray", pulse: false, label: "Pas de chauffage" };
  }
};

interface RadiatorBadgeProps {
  radiatorState: RadiatorStateType | null;
}

export default function RadiatorBadge({ radiatorState }: RadiatorBadgeProps) {
  const { color, pulse, label } = getColorInfo(radiatorState);

  return (
    <div
      className={`${styles.badge} ${styles[color]} ${pulse ? styles.pulse : ""}`}
      title={label}
    >
      <RadiatorIcon className={styles.icon} />
    </div>
  );
}
