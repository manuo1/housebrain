import React from 'react';
import PowerGauge from './PowerGauge/PowerGauge';
import PowerHistoryGraph from './PowerHistoryGraph/PowerHistoryGraph';
import styles from './RealtimePowerMonitor.module.scss';

export default function RealtimePowerMonitor({ maxPower, currentPower }) {
  if (!maxPower || currentPower === undefined) {
    maxPower = 1;
    currentPower = 0;
  }

  const percent = (currentPower / maxPower) * 100;

  return (
    <div className={styles.monitor}>
      <PowerGauge
        maxPower={maxPower}
        currentPower={currentPower}
        percent={percent}
      />
      <PowerHistoryGraph currentPower={currentPower} maxPower={maxPower} />
    </div>
  );
}
