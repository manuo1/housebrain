export const HeatingMode = {
  TEMPERATURE: 'temp',
  ONOFF: 'onoff',
};

export default class DailyHeatingPlan {
  constructor(raw = {}) {
    this.raw = raw;

    // Date
    this.date = raw.date ?? null;

    // Rooms with their slots
    this.rooms = (raw.rooms ?? []).map((room) => ({
      id: room.room_id ?? null,
      name: room.name ?? 'Unknown',
      slots: (room.slots ?? []).map((slot) => ({
        start: slot.start ?? '00:00',
        end: slot.end ?? '00:00',
        value: slot.value ?? null,
      })),
    }));

    // Validation
    this._validate();
  }

  _validate() {
    if (!this.date) {
      console.warn('DailyHeatingPlan: missing date');
    }

    // Validate rooms
    this.rooms.forEach((room) => {
      if (!room.id) {
        console.warn(`DailyHeatingPlan: room missing id - ${room.name}`);
      }

      // Validate slots
      room.slots.forEach((slot) => {
        if (
          !/^\d{2}:\d{2}$/.test(slot.start) ||
          !/^\d{2}:\d{2}$/.test(slot.end)
        ) {
          console.warn(
            `DailyHeatingPlan: invalid time format in slot for ${room.name}`
          );
        }

        if (slot.value === null) {
          console.warn(`DailyHeatingPlan: slot missing value for ${room.name}`);
        }
      });
    });
  }
}
