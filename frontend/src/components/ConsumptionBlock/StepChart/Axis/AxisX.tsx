import styles from "./AxisX.module.scss";

interface AxisXProps {
  labels: string[];
}

const AxisX = ({ labels }: AxisXProps) => (
  <div className={styles.axisX}>
    {labels.map((label, index) => (
      <div key={index} className={styles.xLabel}>{label}</div>
    ))}
  </div>
);

export default AxisX;
