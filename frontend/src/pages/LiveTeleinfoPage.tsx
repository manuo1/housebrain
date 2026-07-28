import TeleinfoTable from "../components/TeleinfoTable/TeleinfoTable";
import useTeleinfoData from "../hooks/useTeleinfoData";
import styles from "./LiveTeleinfoPage.module.scss";

export default function LiveTeleinfoPage() {
  const { data, error } = useTeleinfoData();

  return (
    <div className={styles.container}>
      {error && <p className={styles.error}>Error: {error}</p>}
      {!data && !error && <p>Loading data...</p>}
      {data && <TeleinfoTable data={data} />}
    </div>
  );
}
