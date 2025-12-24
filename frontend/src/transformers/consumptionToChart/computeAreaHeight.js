/**
 * Calcule la hauteur d'un point du graphique
 * @param {number|null} value - Valeur du point (wh, watt, ou euros)
 * @param {number} maxValue - Valeur maximale de l'axe Y
 * @returns {number} - Hauteur en pourcentage (0-100)
 */
function computeAreaHeight(value, maxValue) {
  // Si valeur null ou max = 0, hauteur = 0
  if (value === null || value === undefined || maxValue <= 0) {
    return 0;
  }

  return (value / maxValue) * 100;
}

export default computeAreaHeight;
