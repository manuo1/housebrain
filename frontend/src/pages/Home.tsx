import { Link } from "react-router-dom";
import RoomsList from "../components/Rooms/RoomsList";
import RealtimePowerMonitor from "../components/RealtimePowerMonitor/RealtimePowerMonitor";
import useTeleinfoData from "../hooks/useTeleinfoData";
import styles from "./Home.module.scss";

export default function Home() {
  const { data: teleinfoData } = useTeleinfoData();

  return (
    <div className={styles.home}>
      <div className={styles.dashboardGrid}>
        <div className={styles.roomsSection}>
          <RoomsList />
        </div>
        <div className={styles.statsSection}>
          {teleinfoData && (
            <div className={styles.powerCard}>
              <div className={styles.tariffBadge}>
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
          <div className={styles.constructionCard}>
            <p className={styles.infoText}>
              Récapitulatif de consommation en cours de construction.
            </p>
            <Link to="/consumption" className={styles.link}>
              <span className={styles.linkIcon}>📈</span>
              Consulter l'historique de consommation
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
