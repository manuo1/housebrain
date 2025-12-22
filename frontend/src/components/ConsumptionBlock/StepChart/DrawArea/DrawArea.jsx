import React from 'react';
import styles from './DrawArea.module.scss';

const DrawArea = () => {
  return (
    <div className={styles.drawArea}>
      {/* Les rectangles (Steps) viendront ici */}
      <div className={styles.placeholder}>Rectangles ici</div>
    </div>
  );
};

export default DrawArea;
