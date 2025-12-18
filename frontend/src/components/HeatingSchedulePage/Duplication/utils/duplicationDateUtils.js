/**
 * Ajoute N jours à une date au format YYYY-MM-DD
 * @param {string} dateStr - Date au format YYYY-MM-DD
 * @param {number} days - Nombre de jours à ajouter (peut être négatif)
 * @returns {string} Date résultante au format YYYY-MM-DD
 */
export const addDays = (dateStr, days) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  date.setDate(date.getDate() + days);
  return date.toISOString().slice(0, 10);
};

/**
 * Formate une date YYYY-MM-DD en DD/MM/YYYY
 * @param {string} dateStr - Date au format YYYY-MM-DD
 * @returns {string} Date formatée DD/MM/YYYY
 */
export const formatDate = (dateStr) => {
  if (!dateStr) return '';
  const [year, month, day] = dateStr.split('-');
  return `${day}/${month}/${year}`;
};

/**
 * Retourne le lundi de la semaine suivante
 * @param {string} dateStr - Date au format YYYY-MM-DD
 * @returns {string} Date du lundi suivant au format YYYY-MM-DD
 */
export const getNextMonday = (dateStr) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  const day = date.getDay(); // 0 = dimanche, 1 = lundi, ..., 6 = samedi
  const jsDay = day === 0 ? 7 : day; // convertir dimanche 0 → 7
  // Calculer combien de jours jusqu'au lundi suivant
  const daysUntilNextMonday = 8 - jsDay; // toujours au moins 1 jour (si on est lundi, +7)
  return addDays(dateStr, daysUntilNextMonday);
};

/**
 * Retourne le lundi de la semaine de la date donnée
 * @param {string} dateStr - Date au format YYYY-MM-DD
 * @returns {string} Date du lundi de la semaine au format YYYY-MM-DD
 */
export const getMondayOfWeek = (dateStr) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  const day = date.getDay(); // 0 = dimanche, 1 = lundi, ..., 6 = samedi
  const jsDay = day === 0 ? 7 : day; // convertir dimanche 0 → 7
  // Reculer au lundi de cette semaine
  const daysToMonday = jsDay - 1;
  return addDays(dateStr, -daysToMonday);
};

/**
 * Retourne le dimanche de la semaine de la date donnée
 * @param {string} dateStr - Date au format YYYY-MM-DD
 * @returns {string} Date du dimanche de la semaine au format YYYY-MM-DD
 */
export const getSundayOfWeek = (dateStr) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  const day = date.getDay(); // 0 = dimanche, 1 = lundi, ..., 6 = samedi
  const jsDay = day === 0 ? 7 : day; // convertir dimanche 0 → 7
  // Avancer jusqu'au dimanche de cette semaine
  const daysToSunday = 7 - jsDay;
  return addDays(dateStr, daysToSunday);
};

/**
 * Retourne les dates de début et fin de semaine (lundi au dimanche) pour une date donnée
 * @param {string} dateStr - Date au format YYYY-MM-DD
 * @returns {Object} Objet contenant les dates au format YYYY-MM-DD et DD/MM/YYYY
 */
export const getWeekRange = (dateStr) => {
  if (!dateStr) return null;

  const monday = getMondayOfWeek(dateStr);
  const sunday = getSundayOfWeek(dateStr);

  return {
    monday,
    sunday,
    mondayText: formatDate(monday),
    sundayText: formatDate(sunday),
  };
};
