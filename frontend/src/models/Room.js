class Heating {
  constructor({ mode, value }) {
    this.mode = mode; // 'thermostat' or 'on_off'
    this.value = value; // Current setpoint string or state
  }
}

class TemperatureMeasurements {
  constructor({ temperature, trend }) {
    this.temperature = temperature; // float or null
    this.trend = trend; // 'up', 'down', 'same', or null
  }
}

class Temperature {
  constructor({ id, mac_short, signal_strength, measurements }) {
    this.id = id;
    this.mac_short = mac_short;
    this.signal_strength = signal_strength; // 1-5 bars
    this.measurements = new TemperatureMeasurements(measurements);
  }
}

class Radiator {
  constructor({ id, state }) {
    this.id = id;
    this.state = state; // 'on', 'off', 'turning_on', 'shutting_down', 'load_shed', 'undefined'
  }
}

class Room {
  constructor({ id, name, heating, temperature, radiator }) {
    this.id = id;
    this.name = name;
    this.heating = new Heating(heating);
    this.temperature = temperature ? new Temperature(temperature) : null;
    this.radiator = radiator ? new Radiator(radiator) : null;
  }
}

export default Room;
export { Heating, TemperatureMeasurements, Temperature, Radiator };
