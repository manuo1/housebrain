export const addDays = (dateStr: string, days: number): string => {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  date.setDate(date.getDate() + days);
  return date.toISOString().slice(0, 10);
};

export const formatDate = (dateStr: string): string => {
  if (!dateStr) return "";
  const [year, month, day] = dateStr.split("-");
  return `${day}/${month}/${year}`;
};

export const getNextMonday = (dateStr: string): string => {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  const day = date.getDay();
  const jsDay = day === 0 ? 7 : day;
  const daysUntilNextMonday = 8 - jsDay;
  return addDays(dateStr, daysUntilNextMonday);
};

export const getMondayOfWeek = (dateStr: string): string => {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  const day = date.getDay();
  const jsDay = day === 0 ? 7 : day;
  return addDays(dateStr, -(jsDay - 1));
};

export const getSundayOfWeek = (dateStr: string): string => {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  const day = date.getDay();
  const jsDay = day === 0 ? 7 : day;
  return addDays(dateStr, 7 - jsDay);
};

export interface WeekRange {
  monday: string;
  sunday: string;
  mondayText: string;
  sundayText: string;
}

export const getWeekRange = (dateStr: string): WeekRange | null => {
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
