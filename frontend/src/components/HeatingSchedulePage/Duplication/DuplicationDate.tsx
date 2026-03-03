import styles from "./DuplicationDate.module.scss";

interface DuplicationDateProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  min?: string;
  max?: string;
}

export default function DuplicationDate({ label, value, onChange, min, max }: DuplicationDateProps) {
  return (
    <div className={styles.duplicationDate}>
      <label htmlFor={label}>{label}</label>
      <input
        type="date"
        id={label}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        min={min}
        max={max}
      />
    </div>
  );
}
