import React from 'react';
import styles from './TimelineHeader.module.scss';

export default function TimelineHeader() {
  return (
    <div className={styles.timelineHeader}>
      <span>00h</span>
      <span>06h</span>
      <span>12h</span>
      <span>18h</span>
      <span>24h</span>
    </div>
  );
}
