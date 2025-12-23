import { formatEuro, formatWh } from '../../utils/format';

/**
 * Génère le contenu du tooltip pour un point
 * @param {Object} point - Point de données brut du backend
 * @returns {Object} - { title: string, content: string[] }
 */
function computeTooltip(point) {
  const {
    start_time,
    end_time,
    average_watt,
    wh,
    euros,
    tarif_period,
    interpolated,
  } = point;

  // Titre : plage horaire
  const title = `${start_time} → ${end_time}`;

  // Contenu : toutes les infos quelque soit le type affiché
  const content = [
    `Puissance moyenne: ${average_watt != null ? `${average_watt} W` : '- W'}`,
    `Consommation: ${wh != null ? formatWh(wh) : '- Wh'}`,
    `Coût: ${euros != null ? formatEuro(euros) : '- €'}`,
    `Période Tarifaire: ${tarif_period ?? '-'}`,
  ];

  // Ajouter l'avertissement si donnée interpolée
  if (interpolated) {
    content.push('⚠️ Donnée manquante, valeur interpolée');
  }

  return {
    title,
    content,
  };
}

export default computeTooltip;
