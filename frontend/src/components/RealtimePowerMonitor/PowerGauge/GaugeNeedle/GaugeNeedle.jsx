import React from 'react';

export default function GaugeNeedle({ percent }) {
  const degrees = (percent / 100) * 180 - 90;

  return (
    <g
      transform={`rotate(${degrees} 50 50)`}
      style={{ transition: 'transform 0.8s ease-out' }}
    >
      <line
        x1="50"
        y1="50"
        x2="50"
        y2="16"
        stroke="#e5e7eb"
        strokeWidth="2"
        strokeOpacity="0.5"
      />
      <circle cx="50" cy="50" r="3" fill="#0f172a" stroke="#3f3f46" />
    </g>
  );
}
