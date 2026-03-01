import styles from "./StepChart.module.scss";
import AxisX from "./Axis/AxisX";
import AxisY from "./Axis/AxisY";
import VerticalGridLines from "./GridLines/VerticalGridLines";
import HorizontalGridLines from "./GridLines/HorizontalGridLines";
import DrawArea from "./DrawArea/DrawArea";
import { ChartData } from "../ConsumptionBlock";

interface StepChartProps {
  data: ChartData | null;
}

const StepChart = ({ data }: StepChartProps) => {
  if (!data) {
    return (
      <div className={styles.stepChart}>
        <AxisY labels={["-", "-"]} />
        <div className={styles.chartArea}>
          <VerticalGridLines count={5} />
          <HorizontalGridLines count={24} />
        </div>
        <AxisX labels={["-", "-"]} />
      </div>
    );
  }

  const { axisY, axisX } = data;

  return (
    <div className={styles.stepChart}>
      <AxisY labels={axisY.labels} />
      <div className={styles.chartArea}>
        <VerticalGridLines count={axisY.labels.length} />
        <HorizontalGridLines count={axisX.labels.length} />
        <DrawArea values={data.values} />
      </div>
      <AxisX labels={axisX.labels} />
    </div>
  );
};

export default StepChart;
