import React from 'react';
import styles from './AxisY.module.scss';

const AxisY = ({ labels, unit }) => {
  return (
    <div className={styles.axisY}>
      {labels.map((label, index) => (
        <div key={index} className={styles.yLabel}>
          {label} {unit}
        </div>
      ))}
    </div>
  );
};

export default AxisY;
