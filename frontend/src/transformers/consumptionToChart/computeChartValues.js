import computePointDimensions from './computePointDimensions';
import computePointColors from './computePointColors';
import computeLineHeight from './computeLineHeight';
import computeTooltip from './computeTooltip';

/**
 * Transforme les données brutes en points pour le graphique
 * @param {Array} data - Tableau de points de données brut du backend
 * @param {number} step - Pas de temps en minutes
 * @param {string} displayType - Type d'affichage ('average_watt', 'wh', ou 'euros')
 * @param {number} maxValue - Valeur maximale de l'axe Y
 * @returns {Array} - Tableau de points formatés pour le graphique
 */
function computeChartValues(data, step, displayType, maxValue) {
  const field = displayType;

  // Transformer chaque point
  const chartValues = data.map((point, index) => {
    const value = point[field];

    // Dimensions
    const { width, area_height } = computePointDimensions(
      step,
      value,
      maxValue
    );

    // Couleurs
    const { area_color, line_color } = computePointColors(
      point.tarif_period,
      displayType,
      value
    );

    // Tooltip
    const tooltip = computeTooltip(point);

    // Line height (besoin du point suivant NON NULL)
    let nextPoint = data[index + 1];
    let nextValue = null;

    // Chercher le prochain point avec une valeur non null
    if (nextPoint) {
      nextValue = nextPoint[field];
      // Si le point suivant est null, on ne calcule pas de line_height
      if (nextValue === null || nextValue === undefined) {
        nextValue = null; // Force à null pour avoir line_height = 0
      }
    }

    const nextHeight =
      nextValue !== null && nextValue !== undefined
        ? computePointDimensions(step, nextValue, maxValue).area_height
        : null;
    const line_height = computeLineHeight(area_height, nextHeight);

    return {
      width,
      area_height,
      area_color,
      line_height,
      line_color,
      tooltip,
    };
  });

  return chartValues;
}

export default computeChartValues;
