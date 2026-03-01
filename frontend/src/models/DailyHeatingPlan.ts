export const HeatingMode = {
  TEMPERATURE: "temp",
  ONOFF: "onoff",
} as const;

export type HeatingModeType = (typeof HeatingMode)[keyof typeof HeatingMode];

interface RawSlot {
  start?: string;
  end?: string;
  value?: number | string | null;
}

interface RawRoom {
  room_id?: number | null;
  name?: string;
  slots?: RawSlot[];
}

interface RawDailyHeatingPlan {
  date?: string | null;
  rooms?: RawRoom[];
}

export interface Slot {
  start: string;
  end: string;
  value: number | string | null;
}

export interface PlanRoom {
  id: number | null;
  name: string;
  slots: Slot[];
}

export default class DailyHeatingPlan {
  raw: RawDailyHeatingPlan;
  date: string | null;
  rooms: PlanRoom[];

  constructor(raw: RawDailyHeatingPlan = {}) {
    this.raw = raw;
    this.date = raw.date ?? null;

    this.rooms = (raw.rooms ?? []).map((room) => ({
      id: room.room_id ?? null,
      name: room.name ?? "Unknown",
      slots: (room.slots ?? []).map((slot) => ({
        start: slot.start ?? "00:00",
        end: slot.end ?? "00:00",
        value: slot.value ?? null,
      })),
    }));

    this._validate();
  }

  _validate(): void {
    if (!this.date) {
      console.warn("DailyHeatingPlan: missing date");
    }

    this.rooms.forEach((room) => {
      if (!room.id) {
        console.warn(`DailyHeatingPlan: room missing id - ${room.name}`);
      }

      room.slots.forEach((slot) => {
        if (!/^\d{2}:\d{2}$/.test(slot.start) || !/^\d{2}:\d{2}$/.test(slot.end)) {
          console.warn(`DailyHeatingPlan: invalid time format in slot for ${room.name}`);
        }
        if (slot.value === null) {
          console.warn(`DailyHeatingPlan: slot missing value for ${room.name}`);
        }
      });
    });
  }
}
