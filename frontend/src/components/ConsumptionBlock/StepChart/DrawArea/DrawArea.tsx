import styles from "./DrawArea.module.scss";
import DataPoint from "./DataPoint/DataPoint";
import { ChartPoint } from "../../../../transformers/consumptionToChart/computeChartValues";

interface DrawAreaProps {
  values: ChartPoint[];
}

const DrawArea = ({ values }: DrawAreaProps) => (
  <div className={styles.drawArea}>
    {values.map((pointData, index) => (
      <DataPoint key={index} pointData={pointData} />
    ))}
  </div>
);

export default DrawArea;
