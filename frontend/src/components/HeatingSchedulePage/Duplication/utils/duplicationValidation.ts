import { PlanRoom } from "../../../../models/DailyHeatingPlan";

type DuplicationMode = "day" | "week";

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
    if (new Date(endDate) <= new Date(startDate)) {
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
    if (diffDays > 365) {
      errors.push("La période ne peut pas dépasser 365 jours");
    }
  }

  return errors;
};
