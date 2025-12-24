/**
 * Génère les labels de l'axe X pour un graphique journalier
 * @param {number} step - Pas de temps en minutes (1, 30, ou 60)
 * @returns {string[]} - Labels des heures
 */
function computeAxisX(step) {
  // Pour les steps journaliers : affichage heure par heure
  if (step === 1 || step === 30 || step === 60) {
    return [
      '00:00',
      '01:00',
      '02:00',
      '03:00',
      '04:00',
      '05:00',
      '06:00',
      '07:00',
      '08:00',
      '09:00',
      '10:00',
      '11:00',
      '12:00',
      '13:00',
      '14:00',
      '15:00',
      '16:00',
      '17:00',
      '18:00',
      '19:00',
      '20:00',
      '21:00',
      '22:00',
      '23:00',
      '24:00',
    ];
  }

  // Pour d'autres steps futurs (semaine, mois, etc.)
  throw new Error(`Unsupported step value: ${step}`);
}

export default computeAxisX;
