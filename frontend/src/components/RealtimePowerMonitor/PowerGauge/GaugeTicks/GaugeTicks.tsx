interface GaugeTicksProps {
  maxPower: number;
}

interface Tick {
  x: number;
  y: number;
  label: string | number;
}

export default function GaugeTicks({ maxPower }: GaugeTicksProps) {
  const radius = 45;
  const offset = 8;
  const tickCount = 5;
  const ticks: Tick[] = [];

  for (let i = 0; i < tickCount; i++) {
    const value = (i / (tickCount - 1)) * maxPower;
    const angle = 180 + i * 45;
    const rad = (angle * Math.PI) / 180;

    ticks.push({
      x: 50 + (radius + offset) * Math.cos(rad),
      y: 50 + (radius + offset) * Math.sin(rad) + 2,
      label: value >= 1000 ? `${Math.round(value / 1000)}k` : Math.round(value),
    });
  }

  return (
    <g>
      {ticks.map((tick, i) => (
        <text key={i} x={tick.x} y={tick.y} textAnchor="middle" fontSize="8" fill="#9ca3af">
          {tick.label}
        </text>
      ))}
    </g>
  );
}
