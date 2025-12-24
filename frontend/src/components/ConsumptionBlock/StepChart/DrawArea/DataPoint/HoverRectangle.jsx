import React, { useState, useRef, useEffect } from 'react';
import styles from './HoverRectangle.module.scss';

const HoverRectangle = ({ tooltip }) => {
  const [isHovered, setIsHovered] = useState(false);
  const [side, setSide] = useState('right');
  const hoverRef = useRef(null);

  useEffect(() => {
    if (!hoverRef.current) return;

    const hoverRect = hoverRef.current.getBoundingClientRect();
    const graphContainer = hoverRef.current.closest('[class*="chartArea"]');

    if (!graphContainer) return;

    const graphRect = graphContainer.getBoundingClientRect();
    const pointX = hoverRect.left - graphRect.left + hoverRect.width / 2;

    // Gauche du graph → tooltip à droite, droite du graph → tooltip à gauche
    setSide(pointX < graphRect.width / 2 ? 'right' : 'left');
  }, []); // Calculé une seule fois au mount

  return (
    <div
      ref={hoverRef}
      className={styles.hoverRectangle}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {isHovered && (
        <div className={`${styles.tooltip} ${styles[side]}`}>
          <div className={styles.tooltipTitle}>{tooltip.title}</div>
          {tooltip.content.map((line, index) => (
            <div key={index} className={styles.tooltipLine}>
              {line}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default HoverRectangle;
