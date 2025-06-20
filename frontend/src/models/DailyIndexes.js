/**
 * Represents a single consumption data point
 */
class DailyConsumptionElement {
  constructor({
    date,
    start_time,
    end_time,
    wh,
    average_watt,
    euros,
    interpolated,
    tarif_period,
  }) {
    this.date = new Date(date);
    this.start_time = start_time;
    this.end_time = end_time;
    this.wh = wh;
    this.average_watt = average_watt;
    this.euros = euros;
    this.interpolated = interpolated;
    this.tarif_period = tarif_period;
  }
}

/**
 * Represents totals for a specific label/category
 */
class TotalByLabel {
  constructor({ wh, euros }) {
    this.wh = wh;
    this.euros = euros;
  }
}

/**
 * Main model for daily consumption data
 */
class DailyIndexes {
  // Allowed step values (matching backend constants)
  static ALLOWED_STEPS = [1, 30, 60];

  constructor(date, step, data, totals = {}) {
    this.date = new Date(date);
    this.step = step;
    this.data = this._parseData(data);
    this.totals = this._parseTotals(totals);
  }

  /**
   * Parse raw data array into DailyConsumptionElement instances
   * @param {Array} rawData
   * @returns {Array<DailyConsumptionElement>}
   */
  _parseData(rawData) {
    if (!Array.isArray(rawData)) {
      console.warn("Data is not an array:", rawData);
      return [];
    }
    return rawData.map((item) => new DailyConsumptionElement(item));
  }

  /**
   * Parse raw totals object into TotalByLabel instances
   * @param {Object} rawTotals
   * @returns {Object}
   */
  _parseTotals(rawTotals) {
    const parsedTotals = {};
    for (const [label, total] of Object.entries(rawTotals)) {
      parsedTotals[label] = new TotalByLabel(total);
    }
    return parsedTotals;
  }

  /**
   * Validate step value
   * @returns {boolean}
   */
  isValidStep() {
    return DailyIndexes.ALLOWED_STEPS.includes(this.step);
  }
}

export default DailyIndexes;
export { DailyConsumptionElement, TotalByLabel };
