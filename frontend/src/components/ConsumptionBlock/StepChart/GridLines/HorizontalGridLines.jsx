import React from 'react';
import styles from './HorizontalGridLines.module.scss';

const HorizontalGridLines = ({ count }) => {
  return (
    <div className={styles.horizontalGridLines}>
      {Array.from({ length: count }, (_, index) => (
        <div key={index} className={styles.gridLine} />
      ))}
    </div>
  );
};

export default HorizontalGridLines;
