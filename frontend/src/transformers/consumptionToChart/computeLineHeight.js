/**
 * Calcule la hauteur de ligne (différence avec le point suivant)
 * @param {number} currentHeight - Hauteur en % du point courant
 * @param {number|null} nextHeight - Hauteur en % du point suivant (ou null si dernier point)
 * @returns {number} - Différence de hauteur (positive, négative, ou 0)
 */
function computeLineHeight(currentHeight, nextHeight) {
  // Si pas de point suivant ou valeur null, line_height = 0
  if (nextHeight === null || nextHeight === undefined) {
    return 0;
  }

  // Différence entre le point suivant et le point courant
  return nextHeight - currentHeight;
}

export default computeLineHeight;
