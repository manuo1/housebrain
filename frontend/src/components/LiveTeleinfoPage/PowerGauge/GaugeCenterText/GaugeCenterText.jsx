import React from 'react';

export default function GaugeCenterText({ currentPower, percent }) {
  // Fonction couleur selon pourcentage
  const getColor = (p) => {
    if (p <= 35) return '#2dd4bf';
    if (p <= 70) return '#facc15';
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
