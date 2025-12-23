import React from 'react';
import styles from './DataPoint.module.scss';
import AreaRectangle from './AreaRectangle';
import HoverRectangle from './HoverRectangle';
import LineRectangle from './LineRectangle';
const DataPoint = ({ pointData }) => {
  const { width, area_height, area_color, line_height, line_color, tooltip } =
    pointData;

  return (
    <div className={styles.dataPoint} style={{ width: `${width}%` }}>
      <LineRectangle
        line_height={line_height}
        line_color={line_color}
        area_height={area_height}
      />

      <AreaRectangle area_height={area_height} area_color={area_color} />

      <HoverRectangle tooltip={tooltip} />
    </div>
  );
};

export default DataPoint;
