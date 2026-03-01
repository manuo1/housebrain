import styles from "./TotalCard.module.scss";

interface TotalCardProps {
  label: string;
  kwh: string;
  euros: string;
}

export default function TotalCard({ label, kwh, euros }: TotalCardProps) {
  return (
    <div className={styles.card}>
      <div className={styles.label}>{label} : </div>
      <div className={styles.kwh}>{kwh}</div>
      <div className={styles.separator}>/</div>
      <div className={styles.euros}>{euros}</div>
    </div>
  );
}
