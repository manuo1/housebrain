/**
 * Palette de couleurs par période tarifaire
 * Les groupes sont mutuellement exclusifs, donc réutilisation des couleurs
 */
export const TARIF_PERIOD_COLORS = {
  // Groupe 1 : Tarif unique (seul sur le graphique)
  'Toutes les Heures': '#3b82f6', // Bleu standard

  // Groupe 2 : Heures Normales + Pointe Mobile (2 couleurs)
  'Heures Normales': '#3b82f6', // Bleu
  'Heures de Pointe Mobile': '#ef4444', // Rouge

  // Groupe 3 : Heures Creuses/Pleines classiques (2 couleurs)
  'Heures Creuses': '#10b981', // Vert (économique)
  'Heures Pleines': '#f59e0b', // Orange (coûteux)

  // Groupe 4 : Tempo - 6 périodes (6 couleurs)
  'Heures Creuses Jours Bleus': '#06b6d4', // Cyan clair (meilleur prix)
  'Heures Pleines Jours Bleus': '#3b82f6', // Bleu

  'Heures Creuses Jours Blancs': '#a855f7', // Violet clair
  'Heures Pleines Jours Blancs': '#8b5cf6', // Violet foncé

  'Heures Creuses Jours Rouges': '#f97316', // Orange
  'Heures Pleines Jours Rouges': '#ef4444', // Rouge (pire prix)
};

/**
 * Couleur par défaut si la période tarifaire est inconnue ou null
 */
export const DEFAULT_COLOR = '#6b7280'; // Gris neutre

/**
 * Nombre de graduations par défaut pour l'axe Y
 */
export const DEFAULT_AXIS_Y_STEPS = 5;
