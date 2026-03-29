import { PlanRoom } from "../../../../models/DailyHeatingPlan";
import { addDays, getMondayOfWeek, getSundayOfWeek, getNextMonday } from "../../../../utils/dateUtils";

type DuplicationMode = "day" | "week";

export const MAX_DUPLICATION_DAYS = 365;

// --- Contraintes de dates pour les datepickers ---

export function getStartDateMin(mode: DuplicationMode, sourceDate: string): string {
  if (mode === "week") return getNextMonday(sourceDate);
  return addDays(sourceDate, 1);
}

export function getEndDateMin(mode: DuplicationMode, startDate: string): string {
  if (!startDate) return "";
  if (mode === "week") return getSundayOfWeek(startDate);
  return startDate;
}

export function getEndDateMax(startDate: string): string {
  if (!startDate) return "";
  return addDays(startDate, MAX_DUPLICATION_DAYS);
}

// --- Snap de date selon le mode semaine ---

export function snapStartDate(mode: DuplicationMode, newDate: string): string {
  if (mode === "week" && newDate) return getMondayOfWeek(newDate);
  return newDate;
}

export function snapEndDate(mode: DuplicationMode, newDate: string): string {
  if (mode === "week" && newDate) return getSundayOfWeek(newDate);
  return newDate;
}

// --- Validation ---

interface ValidationParams {
  mode: DuplicationMode;
  selectedRooms: PlanRoom[];
  sourceDate: string;
  startDate: string;
  endDate: string;
  selectedWeekdays: string[];
}

export const getValidationErrors = ({
  mode,
  selectedRooms,
  sourceDate,
  startDate,
  endDate,
  selectedWeekdays,
}: ValidationParams): string[] => {
  const errors: string[] = [];

  if (selectedRooms.length === 0) {
    errors.push("Aucune pièce sélectionnée");
  }

  if (!startDate) {
    errors.push("Veuillez sélectionner une date de début");
  }

  if (!endDate) {
    errors.push("Veuillez sélectionner une date de fin");
  }

  if (mode === "day" && selectedWeekdays.length === 0) {
    errors.push("Veuillez sélectionner au moins un jour de la semaine");
  }

  if (sourceDate && startDate) {
    if (new Date(startDate) <= new Date(sourceDate)) {
      errors.push("La date de début doit être après la date du planning en cours");
    }
  }

  if (startDate && endDate) {
    if (mode === "day" && new Date(endDate) < new Date(startDate)) {
      errors.push("La date de fin doit être égale ou après la date de début");
    }
    if (mode === "week" && new Date(endDate) <= new Date(startDate)) {
      errors.push("La date de fin doit être après la date de début");
    }
  }

  if (mode === "week" && startDate && endDate) {
    const diffDays = Math.floor(
      (new Date(endDate).getTime() - new Date(startDate).getTime()) / (1000 * 60 * 60 * 24)
    );
    if (diffDays < 6) {
      errors.push("La date de fin doit être au moins 6 jours après le début");
    }
  }

  if (startDate && endDate) {
    const diffDays = Math.floor(
      (new Date(endDate).getTime() - new Date(startDate).getTime()) / (1000 * 60 * 60 * 24)
    );
    if (diffDays > MAX_DUPLICATION_DAYS) {
      errors.push(`La période ne peut pas dépasser ${MAX_DUPLICATION_DAYS} jours`);
    }
  }

  return errors;
};
