import { formatLocalDate } from "../utils/dateUtils";
import { ampereToWatt } from "../utils/consumptionUtils";
import { PTEC_LABELS, OPTARIF_LABELS } from "../constants/teleinfoConstants";

const IMPORTANT_KEYS = [
  "OPTARIF",
  "ISOUSC",
  "PTEC",
  "IINST",
  "IMAX",
  "PAPP",
  "last_read",
];

export default class TeleinfoData {
  constructor(raw = {}) {
    this.raw = raw;

    // Important keys
    this.OPTARIF = raw.OPTARIF ?? null;
    this.ISOUSC = raw.ISOUSC !== undefined ? parseInt(raw.ISOUSC, 10) : null;
    this.PTEC = raw.PTEC ?? null;
    this.IINST = raw.IINST !== undefined ? parseInt(raw.IINST, 10) : null;
    this.IMAX = raw.IMAX !== undefined ? parseInt(raw.IMAX, 10) : null;
    this.PAPP = raw.PAPP !== undefined ? parseInt(raw.PAPP, 10) : null;
    this.last_read =
      raw.last_read !== undefined ? formatLocalDate(raw.last_read) : null;

    // Calculated values
    this.maxPower = this.ISOUSC !== null ? ampereToWatt(this.ISOUSC) : null;
    this.currentPower = this.PAPP !== null ? this.PAPP : null;
    this.OPTARIFLabel =
      this.OPTARIF && OPTARIF_LABELS[this.OPTARIF]
        ? OPTARIF_LABELS[this.OPTARIF]
        : OPTARIF_LABELS["DEFAULT"];
    this.PTECLabel =
      this.PTEC && PTEC_LABELS[this.PTEC]
        ? PTEC_LABELS[this.PTEC]
        : PTEC_LABELS["DEFAULT"];

    // Remaining raw keys that are not handled above
    this.otherData = {};
    for (const [key, value] of Object.entries(raw)) {
      if (!IMPORTANT_KEYS.includes(key) && key !== "ADCO") {
        this.otherData[key] = value;
      }
    }
  }
}
