import styles from "./TypeSelector.module.scss";
import { VALUE_TYPES, ValueType } from "../../../constants/consumptionConstants";

interface TypeSelectorProps {
  value: ValueType["key"];
  onChange: (key: ValueType["key"]) => void;
}

export default function TypeSelector({ value, onChange }: TypeSelectorProps) {
  return (
    <div className={styles.typeSelector}>
      {VALUE_TYPES.map(({ key, label }) => (
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
