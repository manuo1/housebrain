import SimpleDate from "../utils/simpleDate";

export const DayStatus = {
  EMPTY: "empty",
  NORMAL: "normal",
  DIFFERENT: "different",
} as const;

export type DayStatusType = (typeof DayStatus)[keyof typeof DayStatus];

interface RawDay {
  date?: string | null;
  status?: string;
}

interface RawHeatingCalendar {
  year?: number | null;
  month?: number | null;
  today?: string | null;
  days?: RawDay[];
}

export interface CalendarDay {
  date: SimpleDate | null;
  status: DayStatusType;
}

export default class HeatingCalendar {
  raw: RawHeatingCalendar;
  year: number | null;
  month: number | null;
  today: SimpleDate | null;
  days: CalendarDay[];

  constructor(raw: RawHeatingCalendar = {}) {
    this.raw = raw;
    this.year = raw.year ?? null;
    this.month = raw.month ?? null;
    this.today = raw.today ? SimpleDate.fromISODate(raw.today) : null;

    this.days = (raw.days ?? []).map((day) => ({
      date: day.date ? SimpleDate.fromISODate(day.date) : null,
      status: (Object.values(DayStatus).includes(day.status as DayStatusType)
        ? day.status
        : DayStatus.EMPTY) as DayStatusType,
    }));

    this._validate();
  }

  _validate(): void {
    if (!this.year || !this.month) {
      console.warn("HeatingCalendar: missing year or month");
    }

    if (this.month !== null && (this.month < 1 || this.month > 12)) {
      console.error(`HeatingCalendar: invalid month ${this.month}`);
    }

    if (!this.today) {
      console.warn("HeatingCalendar: missing today date");
    }

    this.days.forEach((day) => {
      if (!day.date) {
        console.warn("HeatingCalendar: day missing date");
      }
      if (!Object.values(DayStatus).includes(day.status)) {
        console.warn(`HeatingCalendar: invalid status "${day.status}" for ${day.date?.toISO()}`);
      }
    });
  }
}
