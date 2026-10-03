import styles from "./SlotBarLabel.module.scss";

interface SlotBarLabelProps {
  equipmentName: string | null;
}

export default function SlotBarLabel({ equipmentName }: SlotBarLabelProps) {
  return <div className={styles.slotBarLabel}>{equipmentName}</div>;
}
