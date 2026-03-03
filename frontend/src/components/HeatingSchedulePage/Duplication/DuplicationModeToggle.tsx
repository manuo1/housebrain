import styles from "./DuplicationModeToggle.module.scss";

type DuplicationMode = "day" | "week";

interface DuplicationModeToggleProps {
  mode: DuplicationMode;
  onChange: (mode: DuplicationMode) => void;
}

export default function DuplicationModeToggle({ mode, onChange }: DuplicationModeToggleProps) {
  return (
    <div className={styles.modeToggle}>
      <button className={mode === "day" ? styles.active : ""} onClick={() => onChange("day")}>
        Jours
      </button>
      <div className={styles.separator}></div>
      <button className={mode === "week" ? styles.active : ""} onClick={() => onChange("week")}>
        Semaines
      </button>
    </div>
  );
}
