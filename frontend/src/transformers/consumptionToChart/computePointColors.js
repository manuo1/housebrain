import { TARIF_PERIOD_COLORS, DEFAULT_COLOR } from './constants';

/**
 * Détermine les couleurs d'un point selon sa période tarifaire
 * @param {string|null} tarifPeriod - Période tarifaire du point
 * @returns {Object} - { area_color: string, line_color: string }
 */
function computePointColors(tarifPeriod) {
  // Si pas de période tarifaire, couleur par défaut
  if (!tarifPeriod) {
    return {
      area_color: DEFAULT_COLOR,
      line_color: DEFAULT_COLOR,
    };
  }

  // Récupérer la couleur depuis la map
  const color = TARIF_PERIOD_COLORS[tarifPeriod] || DEFAULT_COLOR;

  // area_color et line_color sont identiques
  return {
    area_color: color,
    line_color: color,
  };
}

export default computePointColors;
