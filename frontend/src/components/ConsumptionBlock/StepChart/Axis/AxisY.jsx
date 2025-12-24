import React from 'react';
import styles from './AxisY.module.scss';

const AxisY = ({ labels }) => {
  const reversedLabels = [...labels].reverse();
  return (
    <div className={styles.axisY}>
      {reversedLabels.map((label, index) => (
        <div key={index} className={styles.yLabel}>
          {label}
        </div>
      ))}
    </div>
  );
};

export default AxisY;
