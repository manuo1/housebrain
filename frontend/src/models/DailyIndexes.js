class DailyIndexes {
  constructor(date, step, data, totals = {}) {
    this.date = date;
    this.step = step;
    this.data = data;
    this.totals = totals;
  }
}

export default DailyIndexes;
