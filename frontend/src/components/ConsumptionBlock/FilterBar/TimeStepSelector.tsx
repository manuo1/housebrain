import styles from "./TimeStepSelector.module.scss";
import { STEP_OPTIONS, StepOption } from "../../../constants/consumptionConstants";

interface TimeStepSelectorProps {
  value: StepOption["key"];
  onChange: (key: StepOption["key"]) => void;
}

export default function TimeStepSelector({ value, onChange }: TimeStepSelectorProps) {
  return (
    <div className={styles.timeStepSelector}>
      {STEP_OPTIONS.map(({ key, label }) => (
        <button
          key={key}
          className={`${styles.button} ${value === key ? styles.active : ""}`}
          onClick={() => onChange(key)}
        >
          {label}
        </button>
      ))}
    </div>
  );
}
