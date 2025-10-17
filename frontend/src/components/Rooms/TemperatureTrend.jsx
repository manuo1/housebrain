import React from 'react';
import styles from './TemperatureTrend.module.scss';

const TREND_SYMBOLS = {
  up: '↑',
  down: '↓',
  same: '→',
};

export default function TemperatureTrend({ trend }) {
  const symbol = TREND_SYMBOLS[trend] || '-';

  return (
    <span className={`${styles.trend} ${styles[trend] || ''}`}>{symbol}</span>
  );
}
