interface DailyConsumptionElementRaw {
  date: string;
  start_time: string;
  end_time: string;
  wh: number | null;
  average_watt: number | null;
  euros: number | null;
  interpolated: boolean;
  tarif_period: string | null;
}

interface TotalByLabelRaw {
  wh: number;
  euros: number;
}

class DailyConsumptionElement {
  date: Date;
  start_time: string;
  end_time: string;
  wh: number | null;
  average_watt: number | null;
  euros: number | null;
  interpolated: boolean;
  tarif_period: string | null;

  constructor({ date, start_time, end_time, wh, average_watt, euros, interpolated, tarif_period }: DailyConsumptionElementRaw) {
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

class TotalByLabel {
  wh: number;
  euros: number;

  constructor({ wh, euros }: TotalByLabelRaw) {
    this.wh = wh;
    this.euros = euros;
  }
}

class DailyIndexes {
  static ALLOWED_STEPS = [1, 30, 60];

  date: Date;
  step: number;
  data: DailyConsumptionElement[];
  totals: Record<string, TotalByLabel>;

  constructor(date: string, step: number, data: DailyConsumptionElementRaw[], totals: Record<string, TotalByLabelRaw> = {}) {
    this.date = new Date(date);
    this.step = step;
    this.data = this._parseData(data);
    this.totals = this._parseTotals(totals);
  }

  _parseData(rawData: DailyConsumptionElementRaw[]): DailyConsumptionElement[] {
    if (!Array.isArray(rawData)) {
      console.warn("Data is not an array:", rawData);
      return [];
    }
    return rawData.map((item) => new DailyConsumptionElement(item));
  }

  _parseTotals(rawTotals: Record<string, TotalByLabelRaw>): Record<string, TotalByLabel> {
    const parsedTotals: Record<string, TotalByLabel> = {};
    for (const [label, total] of Object.entries(rawTotals)) {
      parsedTotals[label] = new TotalByLabel(total);
    }
    return parsedTotals;
  }

  isValidStep(): boolean {
    return DailyIndexes.ALLOWED_STEPS.includes(this.step);
  }
}

export default DailyIndexes;
export { DailyConsumptionElement, TotalByLabel };
export type { DailyConsumptionElementRaw, TotalByLabelRaw };
