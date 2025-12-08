import React from 'react';
import { formatFullDayLabel } from '../../utils/dateUtils';
import styles from './DateHeader.module.scss';

export default function DateHeader({ date }) {
  return <h2 className={styles.dateHeader}>{formatFullDayLabel(date)}</h2>;
}
