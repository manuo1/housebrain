import RoomsList from "../components/Rooms/RoomsList";
import EquipmentList from "../components/Equipment/EquipmentList";
import RealtimePowerMonitor from "../components/RealtimePowerMonitor/RealtimePowerMonitor";
import ConsumptionSummary from "../components/ConsumptionSummary/ConsumptionSummary";
import useTeleinfoData from "../hooks/useTeleinfoData";
import styles from "./Home.module.scss";

export default function Home() {
  const { data: teleinfoData } = useTeleinfoData();

  return (
    <div className={styles.home}>
      <div className={styles.dashboardGrid}>
        <div className={styles.leftColumn}>
          <div className={styles.roomsSection}>
            <RoomsList />
          </div>
          <div className={styles.equipmentSection}>
            <EquipmentList />
          </div>
        </div>
        <div className={styles.statsSection}>
          {teleinfoData && (
            <div className={styles.powerCard}>
              <div className={`${styles.tariffBadge} ${styles[teleinfoData.PTECSeverity]}`}>
                <span className={styles.tariffLabel}>Période tarifaire :</span>
                <span className={styles.tariffValue}>
                  {teleinfoData.PTECLabel || "N/A"}
                </span>
              </div>
              <RealtimePowerMonitor
                maxPower={teleinfoData.maxPower}
                currentPower={teleinfoData.currentPower}
              />
            </div>
          )}
          <ConsumptionSummary />
        </div>
      </div>
    </div>
  );
}
