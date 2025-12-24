import React from 'react';
import styles from './AxisX.module.scss';

const AxisX = ({ labels }) => {
  return (
    <div className={styles.axisX}>
      {labels.map((label, index) => (
        <div key={index} className={styles.xLabel}>
          {label}
        </div>
      ))}
    </div>
  );
};

export default AxisX;
