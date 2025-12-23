import React, { useState } from 'react';
import styles from './HoverRectangle.module.scss';

const HoverRectangle = ({ tooltip }) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <>
      <div
        className={styles.hoverRectangle}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      />

      {isHovered && (
        <div className={styles.tooltip}>
          <div className={styles.tooltipTitle}>{tooltip.title}</div>
          {tooltip.content.map((line, index) => (
            <div key={index} className={styles.tooltipLine}>
              {line}
            </div>
          ))}
        </div>
      )}
    </>
  );
};

export default HoverRectangle;
