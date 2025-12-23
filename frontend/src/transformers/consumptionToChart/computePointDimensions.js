/**
 * Calcule les dimensions d'un point du graphique
 * @param {number} step - Pas de temps en minutes (1, 30, ou 60)
 * @param {number|null} value - Valeur du point (wh, watt, ou euros)
 * @param {number} maxValue - Valeur maximale de l'axe Y
 * @returns {Object} - { width: number, area_height: number }
 */
function computePointDimensions(step, value, maxValue) {
  // Calcul de la largeur selon le step
  // Nombre de points dans 24h : 24*60/step
  const pointsInDay = (24 * 60) / step;
  const width = 100 / pointsInDay;

  // Calcul de la hauteur
  // Si valeur null ou max = 0, hauteur = 0
  let area_height = 0;
  if (value !== null && value !== undefined && maxValue > 0) {
    area_height = (value / maxValue) * 100;
  }

  return {
    width,
    area_height,
  };
}

export default computePointDimensions;
