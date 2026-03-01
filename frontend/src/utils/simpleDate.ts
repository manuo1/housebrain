export default class SimpleDate {
  year: number;
  month: number;
  day: number;
  iso_weekday: number;

  constructor(year: number, month: number, day: number) {
    if (!SimpleDate.isValid(year, month, day)) {
      throw new Error(
        `Invalid date encountered: ${year}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}.`
      );
    }

    this.year = year;
    this.month = month;
    this.day = day;
    this.iso_weekday = SimpleDate.#computeISOWeekday(year, month, day);
  }

  // --- Private helpers ---
  static #isLeap(year: number): boolean {
    return (year % 4 === 0 && year % 100 !== 0) || year % 400 === 0;
  }

  static #getMaxDaysInMonth(month: number, year: number): number {
    if (month === 2) return 28 + (SimpleDate.#isLeap(year) ? 1 : 0);
    const thirtyDaysMonths = [4, 6, 9, 11];
    return thirtyDaysMonths.includes(month) ? 30 : 31;
  }

  static #computeISOWeekday(year: number, month: number, day: number): number {
    let y = year;
    const m = month;
    const d = day;

    const t = [0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4];
    if (m < 3) y -= 1;

    const w =
      (y +
        Math.floor(y / 4) -
        Math.floor(y / 100) +
        Math.floor(y / 400) +
        t[m - 1] +
        d) %
      7;

    return w === 0 ? 7 : w;
  }

  // --- Validation ---
  static isValid(year: number, month: number, day: number): boolean {
    if (
      typeof year !== "number" ||
      typeof month !== "number" ||
      typeof day !== "number"
    )
      return false;
    if (month < 1 || month > 12 || day < 1) return false;
    const maxDays = SimpleDate.#getMaxDaysInMonth(month, year);
    return day <= maxDays;
  }

  // --- String representations ---
  toISO(): string {
    return `${String(this.year).padStart(4, "0")}-${String(this.month).padStart(2, "0")}-${String(this.day).padStart(2, "0")}`;
  }

  toString(): string {
    return this.toISO();
  }

  // --- Factory ---
  static fromISODate(isoString: string): SimpleDate {
    const parts = isoString.split("-").map(Number);
    if (parts.length !== 3) {
      throw new Error(
        `Invalid ISO date format: ${isoString}. Expected YYYY-MM-DD.`
      );
    }
    const [year, month, day] = parts;
    return new SimpleDate(year, month, day);
  }
}
