import styles from "./HorizontalGridLines.module.scss";

interface HorizontalGridLinesProps {
  count: number;
}

const HorizontalGridLines = ({ count }: HorizontalGridLinesProps) => (
  <div className={styles.horizontalGridLines}>
    {Array.from({ length: count }, (_, index) => (
      <div key={index} className={styles.gridLine} />
    ))}
  </div>
);

export default HorizontalGridLines;
