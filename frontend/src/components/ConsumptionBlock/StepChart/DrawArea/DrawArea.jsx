import React from 'react';
import styles from './DrawArea.module.scss';
import DataPoint from './DataPoint/DataPoint';

const DrawArea = ({ values }) => {
  return (
    <div className={styles.drawArea}>
      {values.map((pointData, index) => (
        <DataPoint key={index} pointData={pointData} />
      ))}
    </div>
  );
};

export default DrawArea;
