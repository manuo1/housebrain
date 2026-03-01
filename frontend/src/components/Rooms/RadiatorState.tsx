import styles from "./RadiatorState.module.scss";
import { RadiatorState as RadiatorStateType } from "../../models/Room";

interface StateInfo {
  label: string;
  className: string;
}

const getStateInfo = (state: RadiatorStateType | null): StateInfo => {
  switch (state) {
    case null:
      return { label: "Pas de radiateur", className: "undefined" };
    case "on":
      return { label: "Allumé", className: "on" };
    case "off":
      return { label: "Éteint", className: "off" };
    case "turning_on":
      return { label: "Allumage", className: "turning" };
    case "shutting_down":
      return { label: "Arrêt", className: "turning" };
    case "load_shed":
      return { label: "Délestage", className: "loadShed" };
    default:
      return { label: "Indéfini", className: "undefined" };
  }
};

interface RadiatorStateProps {
  radiatorState: RadiatorStateType | null;
}

export default function RadiatorState({ radiatorState }: RadiatorStateProps) {
  const stateInfo = getStateInfo(radiatorState);

  return (
    <div className={`${styles.radiatorState} ${styles[stateInfo.className]}`}>
      <span className={styles.label}>{stateInfo.label}</span>
    </div>
  );
}
