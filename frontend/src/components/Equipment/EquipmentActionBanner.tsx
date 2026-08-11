import { createPortal } from "react-dom";
import LongPressCountdown from "./LongPressCountdown";
import styles from "./EquipmentActionBanner.module.scss";

interface EquipmentActionBannerProps {
  equipmentName: string;
  pressing: boolean;
  progress: number;
  secondsLeft: number;
  message: string | null; // auth notice or trigger error text
}

export default function EquipmentActionBanner({
  equipmentName,
  pressing,
  progress,
  secondsLeft,
  message,
}: EquipmentActionBannerProps) {
  if (!pressing && !message) return null;

  return createPortal(
    <div className={styles.banner}>
      <span className={styles.name}>{equipmentName}</span>
      {pressing && <LongPressCountdown progress={progress} secondsLeft={secondsLeft} compact />}
      {message && <span className={styles.message}>{message}</span>}
    </div>,
    document.body
  );
}
