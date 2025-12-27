import React, { useEffect, useState } from 'react';
import styles from './PowerHistoryGraph.module.scss';

export default function PowerHistoryGraph({ currentPower, maxPower }) {
  const [history, setHistory] = useState([]);
  const maxPoints = 60;

  useEffect(() => {
    setHistory((prev) => {
      const newHistory = [...prev, currentPower];
      if (newHistory.length > maxPoints) {
        newHistory.shift();
      }
      return newHistory;
    });
  }, [currentPower]);

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
          stroke="#e5e7eb"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeOpacity="0.7"
        />
      </svg>
    </div>
  );
}
