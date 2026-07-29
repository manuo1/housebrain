export const DEFAULT_VOLTAGE = 230;

export const PTEC_LABELS: Record<string, string> = {
  "TH..": "Base",
  "HC..": "Heures Creuses",
  "HP..": "Heures Pleines",
  "HN..": "Heures Normales",
  "PM..": "Pointe Mobile",
  HCJB: "Heures Creuses Jour Bleu",
  HCJW: "Heures Creuses Jour Blanc",
  HCJR: "Heures Creuses Jour Rouge",
  HPJB: "Heures Pleines Jour Bleu",
  HPJW: "Heures Pleines Jour Blanc",
  HPJR: "Heures Pleines Jour Rouge",
  DEFAULT: "Inconnu",
};

export const TELEINFO_LABELS: Record<string, string> = {
  OPTARIF: "Option tarifaire",
  ISOUSC: "Intensité souscrite",
  BASE: "Index option Base",
  HCHC: "Index Heures Creuses",
  HCHP: "Index Heures Pleines",
  EJPHN: "Index EJP Heures Normales",
  EJPHPM: "Index EJP Heures de Pointe Mobile",
  BBRHCJB: "Index Tempo Heures Creuses Jours Bleus",
  BBRHPJB: "Index Tempo Heures Pleines Jours Bleus",
  BBRHCJW: "Index Tempo Heures Creuses Jours Blancs",
  BBRHPJW: "Index Tempo Heures Pleines Jours Blancs",
  BBRHCJR: "Index Tempo Heures Creuses Jours Rouges",
  BBRHPJR: "Index Tempo Heures Pleines Jours Rouges",
  PEJP: "Préavis début EJP",
  PTEC: "Période tarifaire en cours",
  DEMAIN: "Couleur du lendemain",
  IINST: "Intensité instantanée",
  IMAX: "Intensité maximale atteinte",
  ADPS: "Avertissement dépassement puissance souscrite",
  MOTDETAT: "Mot d'état du compteur",
  HHPHC: "Horaire HP/HC",
  PAPP: "Puissance apparente instantanée",
  PMAX: "Puissance maximale triphasée",
};

export const TELEINFO_UNITS: Record<string, string> = {
  ISOUSC: "A",
  IINST: "A",
  IMAX: "A",
  PAPP: "VA",
  PMAX: "VA",
  BASE: "Wh",
  HCHC: "Wh",
  HCHP: "Wh",
  EJPHN: "Wh",
  EJPHPM: "Wh",
  BBRHCJB: "Wh",
  BBRHPJB: "Wh",
  BBRHCJW: "Wh",
  BBRHPJW: "Wh",
  BBRHCJR: "Wh",
  BBRHPJR: "Wh",
};

export const OPTARIF_LABELS: Record<string, string> = {
  BASE: "Base",
  "HC..": "Heures Pleines/Creuses",
  "EJP.": "Effacement Jour de Pointe",
  BBRx: "Tempo",
  DEFAULT: "Option inconnue",
};

export type TarifSeverity = "favorable" | "defavorable" | "neutre";

// Classement HC-like / HP-like d'après le code PTEC lui-même (convention EDF stable,
// indépendante du prix réel du contrat) : Heures Creuses/Normales = favorable,
// Heures Pleines/Pointe Mobile = défavorable, Base = prix unique donc neutre.
export const PTEC_SEVERITY: Record<string, TarifSeverity> = {
  "TH..": "neutre",
  "HC..": "favorable",
  "HP..": "defavorable",
  "HN..": "favorable",
  "PM..": "defavorable",
  HCJB: "favorable",
  HCJW: "favorable",
  HCJR: "favorable",
  HPJB: "defavorable",
  HPJW: "defavorable",
  HPJR: "defavorable",
  DEFAULT: "neutre",
};

// Clés déjà affichées explicitement ailleurs (TeleinfoData + TeleinfoTable) :
// à garder synchronisée avec le mapping explicite de TeleinfoTable.tsx si l'un des deux change.
export const TELEINFO_SPECIAL_KEYS = [
  "OPTARIF",
  "ISOUSC",
  "PTEC",
  "IINST",
  "IMAX",
  "PAPP",
  "last_read",
] as const;
