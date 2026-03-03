import styles from "./SlotBarLabel.module.scss";

interface SlotBarLabelProps {
  roomName: string | null;
}

export default function SlotBarLabel({ roomName }: SlotBarLabelProps) {
  return <div className={styles.slotBarLabel}>{roomName}</div>;
}
