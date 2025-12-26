import React from 'react';

export default function GaugeArc({ percent }) {
  const arcLength = 126;
  const offset = arcLength - (arcLength * percent) / 100;

  return (
    <g>
      {/* Arc de fond */}
      <path
        d="M10 50 A40 40 0 0 1 90 50"
        stroke="#1f2535"
        strokeWidth="10"
        fill="none"
      />

      {/* Gradient */}
      <defs>
        <linearGradient id="gaugeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#2dd4bf" />
          <stop offset="60%" stopColor="#facc15" />
          <stop offset="100%" stopColor="#fb7185" />
        </linearGradient>
      </defs>

      {/* Arc rempli */}
      <path
        d="M10 50 A40 40 0 0 1 90 50"
        stroke="url(#gaugeGrad)"
        strokeWidth="10"
        fill="none"
        strokeDasharray={arcLength}
        strokeDashoffset={offset}
        style={{ transition: 'stroke-dashoffset 0.4s ease' }}
      />
    </g>
  );
}
