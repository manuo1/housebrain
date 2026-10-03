export const SlotType = {
  TEMPERATURE: "temp",
  ONOFF: "onoff",
} as const;

export type SlotTypeType = (typeof SlotType)[keyof typeof SlotType];

interface RawSlot {
  start?: string;
  end?: string;
  value?: number | string | null;
}

interface RawEquipment {
  type?: string;
  id?: number | null;
  name?: string;
  slots?: RawSlot[];
}

export interface RawDailyEquipmentPlan {
  date?: string | null;
  equipments?: RawEquipment[];
}

export interface Slot {
  start: string;
  end: string;
  value: number | string | null;
}

export interface PlanEquipment {
  type: string;
  id: number | null;
  name: string;
  slots: Slot[];
}

export default class DailyEquipmentPlan {
  raw: RawDailyEquipmentPlan;
  date: string | null;
  equipments: PlanEquipment[];

  constructor(raw: RawDailyEquipmentPlan = {}) {
    this.raw = raw;
    this.date = raw.date ?? null;

    this.equipments = (raw.equipments ?? []).map((equipment) => ({
      type: equipment.type ?? "unknown",
      id: equipment.id ?? null,
      name: equipment.name ?? "Unknown",
      slots: (equipment.slots ?? []).map((slot) => ({
        start: slot.start ?? "00:00",
        end: slot.end ?? "00:00",
        value: slot.value ?? null,
      })),
    }));

    this._validate();
  }

  _validate(): void {
    if (!this.date) {
      console.warn("DailyEquipmentPlan: missing date");
    }

    this.equipments.forEach((equipment) => {
      if (!equipment.id) {
        console.warn(`DailyEquipmentPlan: equipment missing id - ${equipment.name}`);
      }

      equipment.slots.forEach((slot) => {
        if (!/^\d{2}:\d{2}$/.test(slot.start) || !/^\d{2}:\d{2}$/.test(slot.end)) {
          console.warn(`DailyEquipmentPlan: invalid time format in slot for ${equipment.name}`);
        }
        if (slot.value === null) {
          console.warn(`DailyEquipmentPlan: slot missing value for ${equipment.name}`);
        }
      });
    });
  }
}
