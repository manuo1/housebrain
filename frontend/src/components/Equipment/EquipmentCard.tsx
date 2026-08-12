import { useState } from "react";
import { useAuth } from "../../contexts/useAuth";
import useLongPress from "../../hooks/useLongPress";
import triggerEquipment from "../../services/triggerEquipment";
import EquipmentActionBanner from "./EquipmentActionBanner";
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
    <>
      <EquipmentActionBanner
        equipmentName={equipment.name}
        pressing={pressing}
        progress={progress}
        secondsLeft={secondsLeft}
        message={showAuthNotice ? "Connexion requise" : triggerError}
      />
      <div
        className={`${styles.equipmentCard} ${!equipment.operational ? styles.unavailable : ""}`}
        onMouseDown={handlePressStart}
        onMouseUp={handlePressEnd}
        onMouseLeave={handlePressEnd}
        onTouchStart={handlePressStart}
        onTouchEnd={handlePressEnd}
        onTouchCancel={handlePressEnd}
      >
        <svg className={styles.holdIcon} viewBox="0 0 24 24" aria-hidden="true">
          <circle cx="12" cy="12" r="9" fill="none" strokeWidth="1.5" />
          <circle cx="12" cy="12" r="3.5" />
        </svg>
        <div className={styles.title}>{equipment.name}</div>
        <div className={styles.state}>
          {equipment.operational ? equipment.state : "Indisponible"}
        </div>
      </div>
    </>
  );
}
