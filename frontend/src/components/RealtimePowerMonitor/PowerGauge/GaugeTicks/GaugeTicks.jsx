import React from 'react';

export default function GaugeTicks({ maxPower }) {
  const radius = 45;
  const offset = 8;
  const tickCount = 5;

  const ticks = [];

  for (let i = 0; i < tickCount; i++) {
    const value = (i / (tickCount - 1)) * maxPower;
    const angle = 180 + i * 45; // De 180° à 360° (soit -180° à 0°)
    const rad = (angle * Math.PI) / 180;

    const x = 50 + (radius + offset) * Math.cos(rad);
    const y = 50 + (radius + offset) * Math.sin(rad) + 2;

    ticks.push({
      x,
      y,
      label: value >= 1000 ? `${Math.round(value / 1000)}k` : Math.round(value),
    });
  }

  return (
    <g>
      {ticks.map((tick, i) => (
        <text
          key={i}
          x={tick.x}
          y={tick.y}
          textAnchor="middle"
          fontSize="8"
          fill="#9ca3af"
        >
          {tick.label}
        </text>
      ))}
    </g>
  );
}
