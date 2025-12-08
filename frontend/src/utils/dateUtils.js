export function formatLocalDate(isoString) {
  if (!isoString) return 'N/A';
  const date = new Date(isoString);
  return date.toLocaleString(undefined, {
    dateStyle: 'short',
    timeStyle: 'medium',
  });
}
/**
 * Get French day name from ISO weekday
 * @param {number} isoWeekday - 1 (Lundi) to 7 (Dimanche)
 * @returns {string}
 */
export function getDayLabel(isoWeekday) {
  const days = {
    1: 'Lundi',
    2: 'Mardi',
    3: 'Mercredi',
    4: 'Jeudi',
    5: 'Vendredi',
    6: 'Samedi',
    7: 'Dimanche',
  };
  return days[isoWeekday] ?? 'N/A';
}

/**
 * Get French day short name from ISO weekday
 * @param {number} isoWeekday - 1 (Lundi) to 7 (Dimanche)
 * @returns {string}
 */
export function getDayShort(isoWeekday) {
  const daysShort = {
    1: 'L',
    2: 'M',
    3: 'M',
    4: 'J',
    5: 'V',
    6: 'S',
    7: 'D',
  };
  return daysShort[isoWeekday] ?? '?';
}

/**
 * Get French month name
 * @param {number} month - 1 (Janvier) to 12 (Décembre)
 * @returns {string}
 */
export function getMonthLabel(month) {
  const months = {
    1: 'Janvier',
    2: 'Février',
    3: 'Mars',
    4: 'Avril',
    5: 'Mai',
    6: 'Juin',
    7: 'Juillet',
    8: 'Août',
    9: 'Septembre',
    10: 'Octobre',
    11: 'Novembre',
    12: 'Décembre',
  };
  return months[month] ?? 'N/A';
}

/**
 * Format SimpleDate as "Lundi 08/12/2025"
 * @param {SimpleDate} simpleDate
 * @returns {string}
 */
export function formatFullDayLabel(simpleDate) {
  if (!simpleDate) return 'N/A';

  const dayLabel = getDayLabel(simpleDate.iso_weekday);
  const day = simpleDate.day.toString().padStart(2, '0');
  const month = simpleDate.month.toString().padStart(2, '0');
  const year = simpleDate.year;

  return `${dayLabel} ${day}/${month}/${year}`;
}
