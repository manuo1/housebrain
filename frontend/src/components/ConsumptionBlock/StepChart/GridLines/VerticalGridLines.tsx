import styles from "./VerticalGridLines.module.scss";

interface VerticalGridLinesProps {
  count: number;
}

const VerticalGridLines = ({ count }: VerticalGridLinesProps) => (
  <div className={styles.verticalGridLines}>
    {Array.from({ length: count }, (_, index) => (
      <div key={index} className={styles.gridLine} />
    ))}
  </div>
);

export default VerticalGridLines;
