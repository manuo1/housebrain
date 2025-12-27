import React, { useEffect, useState } from 'react';
import styles from './PowerHistoryGraph.module.scss';

export default function PowerHistoryGraph({ currentPower, maxPower }) {
  const [history, setHistory] = useState([]);
  const maxPoints = 60; // 60 secondes d'historique

  useEffect(() => {
    // Ajoute un point à chaque changement
    setHistory((prev) => {
      const newHistory = [...prev, currentPower];
      if (newHistory.length > maxPoints) {
        newHistory.shift();
      }
      return newHistory;
    });
  }, [currentPower]);

  // Génère le path SVG
  const generatePath = () => {
    if (history.length === 0) return '';

    const width = 100;
    const height = 40;
    const step = width / (maxPoints - 1);

    let path = '';
    history.forEach((power, i) => {
      const x = i * step;
      const y = height - (power / maxPower) * height;
      path += i === 0 ? `M${x},${y}` : ` L${x},${y}`;
    });

    return path;
  };

  // Couleur selon puissance moyenne
  const getStrokeColor = () => {
    if (history.length === 0) return '#2dd4bf';
    const avg = history.reduce((a, b) => a + b, 0) / history.length;
    const percent = (avg / maxPower) * 100;

    if (percent <= 30) return '#2dd4bf'; // Cyan
    if (percent <= 60) return '#facc15'; // Jaune
    return '#fb7185'; // Rose
  };

  return (
    <div className={styles.graphContainer}>
      <svg viewBox="0 0 100 40" className={styles.svg}>
        {/* Grille de fond */}
        <defs>
          <pattern
            id="grid"
            width="10"
            height="10"
            patternUnits="userSpaceOnUse"
          >
            <path
              d="M 10 0 L 0 0 0 10"
              fill="none"
              stroke="#1f2535"
              strokeWidth="0.5"
            />
          </pattern>
        </defs>
        <rect width="100" height="40" fill="url(#grid)" />

        {/* Ligne du graphe */}
        <path
          d={generatePath()}
          fill="none"
          stroke={getStrokeColor()}
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          style={{ transition: 'stroke 0.4s ease' }}
        />
      </svg>
    </div>
  );
}
