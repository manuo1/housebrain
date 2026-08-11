import styles from "./EquipmentCard.module.scss";
import Equipment from "../../models/Equipment";

interface EquipmentCardProps {
  equipment: Equipment;
}

export default function EquipmentCard({ equipment }: EquipmentCardProps) {
  return (
    <div
      className={`${styles.equipmentCard} ${!equipment.operational ? styles.unavailable : ""}`}
    >
      <div className={styles.title}>{equipment.name}</div>
      <div className={styles.state}>
        {equipment.operational ? equipment.state : "Indisponible"}
      </div>
    </div>
  );
}
