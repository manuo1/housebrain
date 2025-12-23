import computeAxisX from './computeAxisX';
import computeAxisY from './computeAxisY';
import computeChartValues from './computeChartValues';

/**
 * Transforme un objet DailyConsumption en format chart
 * @param {DailyConsumption} dailyConsumption - Données brutes du backend
 * @param {string} displayType - Type d'affichage ('watt', 'wh', ou 'euros')
 * @returns {Object} - Données formatées pour StepChart
 */
function transformDailyConsumptionToChart(
  dailyConsumption,
  displayType = 'wh'
) {
  if (!dailyConsumption || !dailyConsumption.data) {
    throw new Error('Invalid DailyConsumption object');
  }

  const { step, data } = dailyConsumption;

  // Calcul de l'axe X
  const axisX = {
    labels: computeAxisX(step),
  };

  // Calcul de l'axe Y
  const { labels, max } = computeAxisY(data, displayType);
  const axisY = { labels };

  // Calcul des points du graphique
  const values = computeChartValues(data, step, displayType, max);

  return {
    axisY,
    axisX,
    values,
  };
}

export default transformDailyConsumptionToChart;
