export function findNiceStep(max: number, targetSteps: number = 5): number {
  if (max === 0) return 1;

  const rawStep = max / targetSteps;
  const magnitude = Math.pow(10, Math.floor(Math.log10(rawStep)));
  const normalized = rawStep / magnitude;

  let niceNormalized: number;
  if (normalized <= 1) niceNormalized = 1;
  else if (normalized <= 2) niceNormalized = 2;
  else if (normalized <= 5) niceNormalized = 5;
  else niceNormalized = 10;

  return niceNormalized * magnitude;
}

export function roundToNiceNumber(value: number): number {
  if (value === 0) return 10;

  const magnitude = Math.pow(10, Math.floor(Math.log10(value)));
  const niceMultiples = [1, 2, 5, 10];

  for (const multiple of niceMultiples) {
    const step = multiple * magnitude;
    const rounded = Math.ceil(value / step) * step;
    if (rounded >= value) return rounded;
  }

  return Math.ceil(value / magnitude) * magnitude;
}
