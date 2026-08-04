import styles from "./StepChart.module.scss";
import AxisX from "./Axis/AxisX";
import AxisY from "./Axis/AxisY";
import VerticalGridLines from "./GridLines/VerticalGridLines";
import HorizontalGridLines from "./GridLines/HorizontalGridLines";
import DrawArea from "./DrawArea/DrawArea";
import { ChartData } from "../ConsumptionBlock";

interface StepChartProps {
  data: ChartData | null;
  isLoading?: boolean;
}

const StepChart = ({ data, isLoading = false }: StepChartProps) => {
  if (!data) {
    return (
      <div className={styles.stepChart}>
        <AxisY labels={["-", "-"]} />
        <div className={styles.chartArea}>
          <VerticalGridLines count={24} />
          <HorizontalGridLines count={5} />
        </div>
        <AxisX labels={["-", "-"]} />
      </div>
    );
  }

  const { axisY, axisX } = data;
  const stepChartClassName = isLoading
    ? `${styles.stepChart} ${styles.loading}`
    : styles.stepChart;

  return (
    <div className={stepChartClassName}>
      <AxisY labels={axisY.labels} />
      <div className={styles.chartArea}>
        <VerticalGridLines count={axisX.labels.length} />
        <HorizontalGridLines count={axisY.labels.length} />
        <DrawArea values={data.values} />
      </div>
      <AxisX labels={axisX.labels} />
    </div>
  );
};

export default StepChart;
