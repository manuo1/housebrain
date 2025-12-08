export default class SimpleDate {
  constructor(year, month, day) {
    if (!SimpleDate.isValid(year, month, day)) {
      throw new Error(
        `Invalid date encountered: ${year}-${String(month).padStart(
          2,
          '0'
        )}-${String(day).padStart(2, '0')}.`
      );
    }

    this.year = year;
    this.month = month;
    this.day = day;
    this.iso_weekday = SimpleDate.#computeISOWeekday(year, month, day);
  }

  // --- Private helpers ---
  static #isLeap(year) {
    return (year % 4 === 0 && year % 100 !== 0) || year % 400 === 0;
  }

  static #getMaxDaysInMonth(month, year) {
    if (month === 2) return 28 + (SimpleDate.#isLeap(year) ? 1 : 0);
    // 30 days in Apr, Jun, Sep, Nov; 31 in others
    const thirtyDaysMonths = [4, 6, 9, 11];
    return thirtyDaysMonths.includes(month) ? 30 : 31;
  }
  static #computeISOWeekday(year, month, day) {
    let y = year;
    const m = month;
    const d = day;

    // Sakamoto table
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

    return w === 0 ? 7 : w; // ISO 1–7
  }

  // --- Validation ---
  static isValid(year, month, day) {
    if (
      typeof year !== 'number' ||
      typeof month !== 'number' ||
      typeof day !== 'number'
    )
      return false;
    if (month < 1 || month > 12 || day < 1) return false;
    const maxDays = SimpleDate.#getMaxDaysInMonth(month, year);
    return day <= maxDays;
  }

  // --- String representations ---
  toISO() {
    return `${String(this.year).padStart(4, '0')}-${String(this.month).padStart(
      2,
      '0'
    )}-${String(this.day).padStart(2, '0')}`;
  }

  toString() {
    return this.toISO();
  }

  // --- Factory ---
  static fromISODate(isoString) {
    const parts = isoString.split('-').map(Number);
    if (parts.length !== 3) {
      throw new Error(
        `Invalid ISO date format: ${isoString}. Expected YYYY-MM-DD.`
      );
    }
    const [year, month, day] = parts;
    return new SimpleDate(year, month, day);
  }
}
