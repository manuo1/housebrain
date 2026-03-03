import styles from "./DuplicationApplyButton.module.scss";

interface DuplicationApplyButtonProps {
  onClick: () => void;
  disabled: boolean;
}

export default function DuplicationApplyButton({ onClick, disabled }: DuplicationApplyButtonProps) {
  return (
    <button className={styles.applyButton} onClick={onClick} disabled={disabled}>
      Appliquer la duplication
    </button>
  );
}
