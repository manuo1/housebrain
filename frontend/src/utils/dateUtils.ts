import { SimpleDate } from "./simpleDate";

export function formatLocalDate(isoString: string | null | undefined): string {
  if (!isoString) return "N/A";
  const date = new Date(isoString);
  return date.toLocaleString(undefined, {
    dateStyle: "short",
    timeStyle: "medium",
  });
}

export function getDayLabel(isoWeekday: number): string {
  const days: Record<number, string> = {
    1: "Lundi",
    2: "Mardi",
    3: "Mercredi",
    4: "Jeudi",
    5: "Vendredi",
    6: "Samedi",
    7: "Dimanche",
  };
  return days[isoWeekday] ?? "N/A";
}

export function getDayShort(isoWeekday: number): string {
  const daysShort: Record<number, string> = {
    1: "L",
    2: "M",
    3: "M",
    4: "J",
    5: "V",
    6: "S",
    7: "D",
  };
  return daysShort[isoWeekday] ?? "?";
}

// Source unique clé <-> jour ISO, partagée par WeekdaySelector et DuplicationSummary
export const WEEKDAYS: { key: string; isoWeekday: number }[] = [
  { key: "monday", isoWeekday: 1 },
  { key: "tuesday", isoWeekday: 2 },
  { key: "wednesday", isoWeekday: 3 },
  { key: "thursday", isoWeekday: 4 },
  { key: "friday", isoWeekday: 5 },
  { key: "saturday", isoWeekday: 6 },
  { key: "sunday", isoWeekday: 7 },
];

export function getMonthLabel(month: number): string {
  const months: Record<number, string> = {
    1: "Janvier",
    2: "Février",
    3: "Mars",
    4: "Avril",
    5: "Mai",
    6: "Juin",
    7: "Juillet",
    8: "Août",
    9: "Septembre",
    10: "Octobre",
    11: "Novembre",
    12: "Décembre",
  };
  return months[month] ?? "N/A";
}

export function formatFullDayLabel(simpleDate: SimpleDate | null | undefined): string {
  if (!simpleDate) return "N/A";

  const dayLabel = getDayLabel(simpleDate.iso_weekday);
  const day = simpleDate.day.toString().padStart(2, "0");
  const month = simpleDate.month.toString().padStart(2, "0");
  const year = simpleDate.year;

  return `${dayLabel} ${day}/${month}/${year}`;
}

export function getTodayDate(): string {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export function addDays(dateStr: string, days: number): string {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  date.setDate(date.getDate() + days);
  return date.toISOString().split("T")[0];
}

export function formatDateLong(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString("fr-FR", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

export function formatDateShort(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString("fr-FR");
}

export function formatDateDD_MM_YYYY(dateStr: string): string {
  if (!dateStr) return "";
  const [year, month, day] = dateStr.split("-");
  return `${day}/${month}/${year}`;
}

export function isToday(dateStr: string): boolean {
  return dateStr === getTodayDate();
}

export function isFuture(dateStr: string): boolean {
  return dateStr > getTodayDate();
}

// --- Fonctions semaine (pour la duplication) ---

export function getMondayOfWeek(dateStr: string): string {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  const day = date.getDay();
  const jsDay = day === 0 ? 7 : day;
  return addDays(dateStr, -(jsDay - 1));
}

export function getSundayOfWeek(dateStr: string): string {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  const day = date.getDay();
  const jsDay = day === 0 ? 7 : day;
  return addDays(dateStr, 7 - jsDay);
}

export function getNextMonday(dateStr: string): string {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  const day = date.getDay();
  const jsDay = day === 0 ? 7 : day;
  const daysUntilNextMonday = 8 - jsDay;
  return addDays(dateStr, daysUntilNextMonday);
}

export interface WeekRange {
  monday: string;
  sunday: string;
  mondayText: string;
  sundayText: string;
}

export function getWeekRange(dateStr: string): WeekRange | null {
  if (!dateStr) return null;
  const monday = getMondayOfWeek(dateStr);
  const sunday = getSundayOfWeek(dateStr);
  return {
    monday,
    sunday,
    mondayText: formatDateDD_MM_YYYY(monday),
    sundayText: formatDateDD_MM_YYYY(sunday),
  };
}
