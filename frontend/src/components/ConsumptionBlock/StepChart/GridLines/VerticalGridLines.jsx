import React from 'react';
import styles from './VerticalGridLines.module.scss';

const VerticalGridLines = ({ count }) => {
  return (
    <div className={styles.verticalGridLines}>
      {Array.from({ length: count }, (_, index) => (
        <div key={index} className={styles.gridLine} />
      ))}
    </div>
  );
};

export default VerticalGridLines;
