import { findNiceStep, roundToNiceNumber } from '../../utils/niceNumbers';

function findMaxValue(data, field) {
  const values = data
    .map((point) => point[field])
    .filter((val) => val !== null && val !== undefined);

  if (values.length === 0) return 0;
  return Math.max(...values);
}

function computeAxisY(data, displayType) {
  const unitMap = {
    average_watt: ' W',
    wh: ' Wh',
    euros: ' €',
  };

  const field = displayType;
  const unit = unitMap[displayType];

  if (!unit) {
    throw new Error(`Invalid display type: ${displayType}`);
  }

  // Trouver le max et l'arrondir
  const rawMax = findMaxValue(data, field);
  const roundedMax = roundToNiceNumber(rawMax);

  // Trouver un pas joli
  const step = findNiceStep(roundedMax);

  // Ajuster le max pour qu'il soit un multiple exact du step
  const max = Math.ceil(roundedMax / step) * step;

  // Générer les graduations (toujours régulières)
  const numSteps = max / step;
  const labels = [];

  for (let i = 0; i <= numSteps; i++) {
    let value = i * step;

    // Arrondir pour éviter les problèmes de précision flottante
    if (displayType === 'euros') {
      value = Math.round(value * 100) / 100; // 2 décimales
    } else {
      value = Math.round(value); // Arrondir à l'entier
    }

    labels.push(`${value}${unit}`);
  }

  return { labels, max };
}

export default computeAxisY;
