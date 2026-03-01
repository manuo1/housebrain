import RadiatorState from "./RadiatorState";
import HeatingControl from "./HeatingControl";
import styles from "./HeatingZone.module.scss";
import { HeatingMode, RadiatorState as RadiatorStateType } from "../../models/Room";

interface HeatingZoneProps {
  heatingModeLabel: HeatingMode | null;
  heatingModeValue: string | number | null;
  radiatorState: RadiatorStateType | null;
}

export default function HeatingZone({ heatingModeLabel, heatingModeValue, radiatorState }: HeatingZoneProps) {
  return (
    <fieldset className={styles.heatingZone}>
      <legend className={styles.label}>Chauffage</legend>
      <RadiatorState radiatorState={radiatorState} />
      <HeatingControl
        heatingModeValue={heatingModeValue}
        heatingModeLabel={heatingModeLabel}
      />
    </fieldset>
  );
}
