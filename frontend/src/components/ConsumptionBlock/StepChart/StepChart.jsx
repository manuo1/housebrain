import React from 'react';
import styles from './StepChart.module.scss';
import AxisX from './Axis/AxisX';
import AxisY from './Axis/AxisY';
import VerticalGridLines from './GridLines/VerticalGridLines';
import HorizontalGridLines from './GridLines/HorizontalGridLines';
import DrawArea from './DrawArea/DrawArea';

const StepChart = ({ data }) => {
  const { axisY, axisX } = data;

  return (
    <div className={styles.stepChart}>
      {/* Axe Y - Labels verticaux */}
      <AxisY labels={axisY.labels} />

      {/* Zone du graphique avec grille */}
      <div className={styles.chartArea}>
        {/* Lignes horizontales de grille */}
        <VerticalGridLines count={axisY.labels.length} />

        {/* Lignes verticales de grille */}
        <HorizontalGridLines count={axisX.labels.length} />

        {/* Zone de dessin des rectangles */}
        <DrawArea values={data.values} />
      </div>

      {/* Axe X - Labels horizontaux */}
      <AxisX labels={axisX.labels} />
    </div>
  );
};

export default StepChart;
