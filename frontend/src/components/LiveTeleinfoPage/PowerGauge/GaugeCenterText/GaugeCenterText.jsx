import React from 'react';

export default function GaugeCenterText({ currentPower, percent }) {
  // Fonction couleur alignée sur le gradient de l'arc
  const getColor = (p) => {
    if (p <= 60) {
      // Interpolation cyan (#2dd4bf) → jaune (#facc15)
      const ratio = p / 60;
      if (ratio < 0.5) return '#2dd4bf'; // Cyan jusqu'à 30%
      return '#facc15'; // Jaune de 30% à 60%
    }
    // Rose après 60%
    return '#fb7185';
  };

  const color = getColor(percent);

  return (
    <text
      x="50"
      y="38"
      textAnchor="middle"
      fill={color}
      fontSize="11"
      fontWeight="600"
      style={{ transition: 'fill 0.4s ease' }}
    >
      {currentPower} W
    </text>
  );
}
