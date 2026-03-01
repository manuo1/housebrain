export type HeatingMode = "thermostat" | "on_off";
export type TemperatureTrend = "up" | "down" | "same" | null;
export type RadiatorState = "on" | "off" | "turning_on" | "shutting_down" | "load_shed" | "undefined";

interface HeatingRaw {
  mode: HeatingMode;
  value: string | number | null;
}

interface TemperatureMeasurementsRaw {
  temperature: number | null;
  trend: TemperatureTrend;
}

interface TemperatureRaw {
  id: number;
  mac_short: string;
  signal_strength: number;
  measurements: TemperatureMeasurementsRaw;
}

interface RadiatorRaw {
  id: number;
  state: RadiatorState;
}

interface RoomRaw {
  id: number;
  name: string;
  heating: HeatingRaw;
  temperature: TemperatureRaw;
  radiator: RadiatorRaw;
}

class Heating {
  mode: HeatingMode;
  value: string | number | null;

  constructor({ mode, value }: HeatingRaw) {
    this.mode = mode;
    this.value = value;
  }
}

class TemperatureMeasurements {
  temperature: number | null;
  trend: TemperatureTrend;

  constructor({ temperature, trend }: TemperatureMeasurementsRaw) {
    this.temperature = temperature;
    this.trend = trend;
  }
}

class Temperature {
  id: number;
  mac_short: string;
  signal_strength: number;
  measurements: TemperatureMeasurements;

  constructor({ id, mac_short, signal_strength, measurements }: TemperatureRaw) {
    this.id = id;
    this.mac_short = mac_short;
    this.signal_strength = signal_strength;
    this.measurements = new TemperatureMeasurements(measurements);
  }
}

class Radiator {
  id: number;
  state: RadiatorState;

  constructor({ id, state }: RadiatorRaw) {
    this.id = id;
    this.state = state;
  }
}

class Room {
  id: number;
  name: string;
  heating: Heating;
  temperature: Temperature;
  radiator: Radiator;

  constructor({ id, name, heating, temperature, radiator }: RoomRaw) {
    this.id = id;
    this.name = name;
    this.heating = new Heating(heating);
    this.temperature = new Temperature(temperature);
    this.radiator = new Radiator(radiator);
  }
}

export default Room;
export { Heating, TemperatureMeasurements, Temperature, Radiator };
export type { HeatingRaw, TemperatureMeasurementsRaw, TemperatureRaw, RadiatorRaw, RoomRaw };
