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
  return new Date().toISOString().split("T")[0];
}

export function addDays(dateStr: string, days: number): string {
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

export function isToday(dateStr: string): boolean {
  return dateStr === getTodayDate();
}

export function isFuture(dateStr: string): boolean {
  return dateStr > getTodayDate();
}
