import React from 'react';
import styles from './TimelineHeader.module.scss';

export default function TimelineHeader() {
  return (
    <div className={styles.timelineHeader}>
      <span>00H</span>
      <span>02H</span>
      <span>04H</span>
      <span>06H</span>
      <span>08H</span>
      <span>10H</span>
      <span>12H</span>
      <span>14H</span>
      <span>16H</span>
      <span>18H</span>
      <span>20H</span>
      <span>22H</span>
      <span>24H</span>
    </div>
  );
}
