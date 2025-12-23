/**
 * Trouve un "pas joli" pour diviser un maximum en graduations lisibles
 * @param {number} max - Valeur maximale
 * @param {number} targetSteps - Nombre de graduations souhaité (environ)
 * @returns {number} - Pas à utiliser
 */
export function findNiceStep(max, targetSteps = 5) {
  if (max === 0) return 1;

  // Calculer un pas brut
  const rawStep = max / targetSteps;

  // Trouver l'ordre de grandeur
  const magnitude = Math.pow(10, Math.floor(Math.log10(rawStep)));

  // Normaliser le pas (entre 1 et 10)
  const normalized = rawStep / magnitude;

  // Choisir le "joli" nombre le plus proche : 1, 2, 5, ou 10
  let niceNormalized;
  if (normalized <= 1) niceNormalized = 1;
  else if (normalized <= 2) niceNormalized = 2;
  else if (normalized <= 5) niceNormalized = 5;
  else niceNormalized = 10;

  // Revenir à l'échelle réelle
  return niceNormalized * magnitude;
}

/**
 * Arrondit une valeur au multiple supérieur "joli"
 * @param {number} value - Valeur à arrondir
 * @returns {number} - Valeur arrondie
 */
export function roundToNiceNumber(value) {
  if (value === 0) return 10;

  const magnitude = Math.pow(10, Math.floor(Math.log10(value)));

  // Multiples "jolis" : 1, 2, 5
  const niceMultiples = [1, 2, 5, 10];

  for (const multiple of niceMultiples) {
    const step = multiple * magnitude;
    const rounded = Math.ceil(value / step) * step;
    if (rounded >= value) return rounded;
  }

  return Math.ceil(value / magnitude) * magnitude;
}
