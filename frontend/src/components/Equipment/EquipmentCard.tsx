import { useState } from "react";
import { useAuth } from "../../contexts/useAuth";
import useLongPress from "../../hooks/useLongPress";
import triggerEquipment from "../../services/triggerEquipment";
import LongPressCountdown from "./LongPressCountdown";
import styles from "./EquipmentCard.module.scss";
import Equipment from "../../models/Equipment";

interface EquipmentCardProps {
  equipment: Equipment;
}

export default function EquipmentCard({ equipment }: EquipmentCardProps) {
  const { user, accessToken, refresh } = useAuth();
  const [showAuthNotice, setShowAuthNotice] = useState(false);
  const [triggerError, setTriggerError] = useState<string | null>(null);

  const { pressing, progress, secondsLeft, handlers } = useLongPress({
    durationMs: 5000,
    onComplete: async () => {
      if (!accessToken) return;
      try {
        await triggerEquipment(equipment.id, accessToken, refresh);
      } catch (err) {
        console.error(err);
        setTriggerError("Erreur lors du déclenchement");
        setTimeout(() => setTriggerError(null), 3000);
      }
    },
  });

  const handlePressStart = () => {
    if (!user) {
      setShowAuthNotice(true);
      return;
    }
    handlers.onMouseDown();
  };

  const handlePressEnd = () => {
    setShowAuthNotice(false);
    handlers.onMouseUp();
  };

  return (
    <div
      className={`${styles.equipmentCard} ${!equipment.operational ? styles.unavailable : ""}`}
      onMouseDown={handlePressStart}
      onMouseUp={handlePressEnd}
      onMouseLeave={handlePressEnd}
      onTouchStart={handlePressStart}
      onTouchEnd={handlePressEnd}
      onTouchCancel={handlePressEnd}
    >
      {pressing && <LongPressCountdown progress={progress} secondsLeft={secondsLeft} />}
      {showAuthNotice && (
        <div className={styles.authNotice}>Connexion requise</div>
      )}
      {triggerError && (
        <div className={styles.authNotice}>{triggerError}</div>
      )}
      <div className={styles.title}>{equipment.name}</div>
      <div className={styles.state}>
        {equipment.operational ? equipment.state : "Indisponible"}
      </div>
    </div>
  );
}
