import styles from "./AxisY.module.scss";

interface AxisYProps {
  labels: string[];
}

const AxisY = ({ labels }: AxisYProps) => {
  const reversedLabels = [...labels].reverse();
  return (
    <div className={styles.axisY}>
      {reversedLabels.map((label, index) => (
        <div key={index} className={styles.yLabel}>{label}</div>
      ))}
    </div>
  );
};

export default AxisY;
