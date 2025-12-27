// Couleur selon pourcentage (alignée sur gradient)
export function getGaugeColor(percent) {
  if (percent <= 30) return '#2dd4bf'; // Cyan
  if (percent <= 60) return '#facc15'; // Jaune
  return '#fb7185'; // Rose
}

// Calcul des degrés pour l'aiguille
export function percentToDegrees(percent) {
  return (percent / 100) * 180 - 90;
}

// Calcul du dashoffset pour l'arc
export function percentToArcOffset(percent, arcLength = 126) {
  return arcLength - (arcLength * percent) / 100;
}
