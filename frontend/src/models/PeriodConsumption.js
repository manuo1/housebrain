class ConsumptionValue {
  constructor({ wh, euros }) {
    this.wh = wh;
    this.euros = euros;
  }
}

class PeriodItem {
  constructor({ start_date, end_date, consumption }) {
    this.startDate = new Date(start_date);
    this.endDate = new Date(end_date);
    this.consumption = this._parseConsumption(consumption);
  }

  _parseConsumption(raw) {
    const parsed = {};
    for (const [label, value] of Object.entries(raw)) {
      parsed[label] = new ConsumptionValue(value);
    }
    return parsed;
  }

  get total() {
    return this.consumption["Total"] || null;
  }
}

class PeriodConsumption {
  constructor({ start_date, end_date, period, data, totals }) {
    this.startDate = new Date(start_date);
    this.endDate = new Date(end_date);
    this.period = period;
    this.data = this._parseData(data);
    this.totals = this._parseTotals(totals);
  }

  _parseData(dataList) {
    return Array.isArray(dataList)
      ? dataList.map((item) => new PeriodItem(item))
      : [];
  }

  _parseTotals(rawTotals) {
    const parsed = {};
    for (const [label, value] of Object.entries(rawTotals || {})) {
      parsed[label] = new ConsumptionValue(value);
    }
    return parsed;
  }

  getTotalForLabel(label) {
    return this.totals[label] || null;
  }
}

export default PeriodConsumption;
export { PeriodItem, ConsumptionValue };
