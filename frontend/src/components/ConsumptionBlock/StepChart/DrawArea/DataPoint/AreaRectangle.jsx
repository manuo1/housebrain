import React from 'react';
import styles from './AreaRectangle.module.scss';

const AreaRectangle = ({ area_height, area_color }) => {
  const style = { height: `${area_height}%`, opacity: 0.5 };
  if (area_color) {
    style.backgroundColor = area_color;
  }

  return <div className={styles.areaRectangle} style={style} />;
};

export default AreaRectangle;
