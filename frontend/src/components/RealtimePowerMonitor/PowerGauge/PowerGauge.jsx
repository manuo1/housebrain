import React from 'react';
import GaugeArc from './GaugeArc/GaugeArc';
import GaugeNeedle from './GaugeNeedle/GaugeNeedle';
import GaugeCenterText from './GaugeCenterText/GaugeCenterText';
import GaugeTicks from './GaugeTicks/GaugeTicks';
import styles from './PowerGauge.module.scss';

export default function PowerGauge({ maxPower, currentPower, percent }) {
  return (
    <div className={styles.gaugeContainer}>
      {/* SVG de l'aiguille (derrière) */}
      <svg viewBox="0 0 100 60" className={styles.svg}>
        <GaugeNeedle percent={percent} />
      </svg>

      {/* SVG de l'arc + texte + graduations (devant) */}
      <svg viewBox="0 0 100 60" className={styles.svg}>
        <GaugeArc percent={percent} />
        <GaugeCenterText currentPower={currentPower} percent={percent} />
        <GaugeTicks maxPower={maxPower} />
      </svg>
    </div>
  );
}
