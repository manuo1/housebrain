/**
 * Valide les paramètres de duplication et retourne la liste des erreurs
 * @param {Object} params - Paramètres de validation
 * @param {string} params.mode - Mode de duplication ('day' ou 'week')
 * @param {Array} params.selectedRooms - Liste des pièces sélectionnées
 * @param {string} params.sourceDate - Date source au format YYYY-MM-DD
 * @param {string} params.startDate - Date de début au format YYYY-MM-DD
 * @param {string} params.endDate - Date de fin au format YYYY-MM-DD
 * @param {Array} params.selectedWeekdays - Jours de la semaine sélectionnés (en mode 'day')
 * @returns {Array<string>} Liste des messages d'erreur
 */
export const getValidationErrors = ({
  mode,
  selectedRooms,
  sourceDate,
  startDate,
  endDate,
  selectedWeekdays,
}) => {
  const errors = [];

  // 1. Rooms vides
  if (selectedRooms.length === 0) {
    errors.push('Aucune pièce sélectionnée');
  }

  // 2. StartDate manquante
  if (!startDate) {
    errors.push('Veuillez sélectionner une date de début');
  }

  // 3. EndDate manquante
  if (!endDate) {
    errors.push('Veuillez sélectionner une date de fin');
  }

  // 4. Weekdays vides en mode day
  if (mode === 'day' && selectedWeekdays.length === 0) {
    errors.push('Veuillez sélectionner au moins un jour de la semaine');
  }

  // 5. StartDate doit être supérieur à sourceDate
  if (sourceDate && startDate) {
    const source = new Date(sourceDate);
    const start = new Date(startDate);
    if (start <= source) {
      errors.push(
        'La date de début doit être après la date du planning en cours'
      );
    }
  }

  // 6. EndDate doit être strictement supérieur à startDate
  if (startDate && endDate) {
    const start = new Date(startDate);
    const end = new Date(endDate);
    if (end <= start) {
      errors.push('La date de fin doit être après la date de début');
    }
  }

  // 7. Mode week : vérifier semaine différente (entre start et end)
  if (mode === 'week' && startDate && endDate) {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const diffDays = Math.floor((end - start) / (1000 * 60 * 60 * 24));
    if (diffDays < 6) {
      errors.push('La date de fin doit être au moins 6 jours après le début');
    }
  }

  // 8. Max 365 jours (entre start et end)
  if (startDate && endDate) {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const diffDays = Math.floor((end - start) / (1000 * 60 * 60 * 24));
    if (diffDays > 365) {
      errors.push('La période ne peut pas dépasser 365 jours');
    }
  }

  return errors;
};
