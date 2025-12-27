import React from 'react';
import { getGaugeColor } from '../../utils/gaugeUtils';

export default function GaugeCenterText({ currentPower, percent }) {
  const color = getGaugeColor(percent);

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
