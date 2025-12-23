import { findNiceStep, roundToNiceNumber } from '../../utils/niceNumbers';

function findMaxValue(data, field) {
  const values = data
    .map((point) => point[field])
    .filter((val) => val !== null && val !== undefined);

  if (values.length === 0) return 0;
  return Math.max(...values);
}

function computeAxisY(data, displayType) {
  const fieldMap = {
    watt: 'average_watt',
    wh: 'wh',
    euros: 'euros',
  };

  const unitMap = {
    watt: ' W',
    wh: ' Wh',
    euros: ' €',
  };

  const field = fieldMap[displayType];
  const unit = unitMap[displayType];

  if (!field) {
    throw new Error(`Invalid display type: ${displayType}`);
  }

  // Trouver le max et l'arrondir
  const rawMax = findMaxValue(data, field);
  const roundedMax = roundToNiceNumber(rawMax);

  // Trouver un pas joli
  const step = findNiceStep(roundedMax);

  // Ajuster le max pour qu'il soit un multiple exact du step
  const max = Math.ceil(roundedMax / step) * step;

  // Générer les graduations (toujours régulières maintenant)
  const numSteps = max / step;
  const labels = [];

  for (let i = 0; i <= numSteps; i++) {
    const value = i * step;
    labels.push(`${value}${unit}`);
  }

  return { labels, max };
}

export default computeAxisY;
