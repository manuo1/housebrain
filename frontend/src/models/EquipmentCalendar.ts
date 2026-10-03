import SimpleDate from "../utils/simpleDate";

interface RawDay {
  date?: string | null;
}

interface RawEquipmentCalendar {
  year?: number | null;
  month?: number | null;
  today?: string | null;
  days?: RawDay[];
}

export interface CalendarDay {
  date: SimpleDate | null;
}

export default class EquipmentCalendar {
  raw: RawEquipmentCalendar;
  year: number | null;
  month: number | null;
  today: SimpleDate | null;
  days: CalendarDay[];

  constructor(raw: RawEquipmentCalendar = {}) {
    this.raw = raw;
    this.year = raw.year ?? null;
    this.month = raw.month ?? null;
    this.today = raw.today ? SimpleDate.fromISODate(raw.today) : null;

    this.days = (raw.days ?? []).map((day) => ({
      date: day.date ? SimpleDate.fromISODate(day.date) : null,
    }));

    this._validate();
  }

  _validate(): void {
    if (!this.year || !this.month) {
      console.warn("EquipmentCalendar: missing year or month");
    }

    if (this.month !== null && (this.month < 1 || this.month > 12)) {
      console.error(`EquipmentCalendar: invalid month ${this.month}`);
    }

    if (!this.today) {
      console.warn("EquipmentCalendar: missing today date");
    }

    this.days.forEach((day) => {
      if (!day.date) {
        console.warn("EquipmentCalendar: day missing date");
      }
    });
  }
}
