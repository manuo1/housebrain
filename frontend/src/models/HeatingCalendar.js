import SimpleDate from '../utils/simpleDate';

export const DayStatus = {
  EMPTY: 'empty',
  NORMAL: 'normal',
  DIFFERENT: 'different',
};

export default class HeatingCalendar {
  constructor(raw = {}) {
    this.raw = raw;

    // Metadata
    this.year = raw.year ?? null;
    this.month = raw.month ?? null;

    // Today from backend
    this.today = raw.today ? SimpleDate.fromISODate(raw.today) : null;

    // Days array (parsed as SimpleDate objects with status)
    this.days = (raw.days ?? []).map((day) => ({
      date: day.date ? SimpleDate.fromISODate(day.date) : null,
      status: day.status ?? DayStatus.EMPTY,
    }));

    // Validation
    this._validate();
  }

  _validate() {
    if (!this.year || !this.month) {
      console.warn('HeatingCalendar: missing year or month');
    }

    if (this.month < 1 || this.month > 12) {
      console.error(`HeatingCalendar: invalid month ${this.month}`);
    }

    if (!this.today) {
      console.warn('HeatingCalendar: missing today date');
    }

    // Validate days
    this.days.forEach((day) => {
      if (!day.date) {
        console.warn('HeatingCalendar: day missing date');
      }

      if (!Object.values(DayStatus).includes(day.status)) {
        console.warn(
          `HeatingCalendar: invalid status "${
            day.status
          }" for ${day.date?.toISO()}`
        );
      }
    });
  }
}
