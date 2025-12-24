import { TARIF_PERIOD_COLORS, DEFAULT_COLOR } from './constants';

/**
 * Détermine les couleurs d'un point selon sa période tarifaire et le type d'affichage
 * @param {string|null} tarifPeriod - Période tarifaire du point
 * @param {string} displayType - Type d'affichage ('average_watt', 'wh', ou 'euros')
 * @param {*} value - Valeur du point (pour détecter null)
 * @returns {Object} - { area_color: string, line_color: string }
 */
function computePointColors(tarifPeriod, displayType, value) {
  // Si valeur null : tout transparent (donnée manquante)
  if (value === null || value === undefined) {
    return {
      area_color: 'transparent',
      line_color: 'transparent',
    };
  }

  // Si pas de période tarifaire, couleur par défaut
  if (!tarifPeriod) {
    return {
      area_color:
        displayType === 'average_watt' ? 'transparent' : DEFAULT_COLOR,
      line_color: DEFAULT_COLOR,
    };
  }

  // Récupérer la couleur depuis la map
  const color = TARIF_PERIOD_COLORS[tarifPeriod] || DEFAULT_COLOR;

  // Pour les watts : pas de remplissage, juste la ligne
  // Pour wh et euros : remplissage + ligne de la même couleur
  return {
    area_color: displayType === 'average_watt' ? 'transparent' : color,
    line_color: color,
  };
}

export default computePointColors;
