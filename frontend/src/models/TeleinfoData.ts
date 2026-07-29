import { formatLocalDate } from "../utils/dateUtils";
import { ampereToWatt } from "../utils/teleinfoUtils";
import { PTEC_LABELS, OPTARIF_LABELS, PTEC_SEVERITY, TarifSeverity, TELEINFO_SPECIAL_KEYS } from "../constants/teleinfoConstants";

interface RawTeleinfoData {
  OPTARIF?: string | null;
  ISOUSC?: string | number;
  PTEC?: string | null;
  IINST?: string | number;
  IMAX?: string | number;
  PAPP?: string | number;
  last_read?: string;
  [key: string]: string | number | null | undefined;
}

export default class TeleinfoData {
  raw: RawTeleinfoData;
  OPTARIF: string | null;
  ISOUSC: number | null;
  PTEC: string | null;
  IINST: number | null;
  IMAX: number | null;
  PAPP: number | null;
  last_read: string | null;
  maxPower: number | null;
  currentPower: number | null;
  OPTARIFLabel: string;
  PTECLabel: string;
  PTECSeverity: TarifSeverity;
  otherData: Record<string, string | number | null | undefined>;

  constructor(raw: RawTeleinfoData = {}) {
    this.raw = raw;

    this.OPTARIF = raw.OPTARIF ?? null;
    this.ISOUSC = raw.ISOUSC !== undefined ? parseInt(String(raw.ISOUSC), 10) : null;
    this.PTEC = raw.PTEC ?? null;
    this.IINST = raw.IINST !== undefined ? parseInt(String(raw.IINST), 10) : null;
    this.IMAX = raw.IMAX !== undefined ? parseInt(String(raw.IMAX), 10) : null;
    this.PAPP = raw.PAPP !== undefined ? parseInt(String(raw.PAPP), 10) : null;
    this.last_read = raw.last_read !== undefined ? formatLocalDate(raw.last_read) : null;

    this.maxPower = this.ISOUSC !== null ? ampereToWatt(this.ISOUSC) : null;
    this.currentPower = this.PAPP !== null ? this.PAPP : null;
    this.OPTARIFLabel = this.OPTARIF && OPTARIF_LABELS[this.OPTARIF]
      ? OPTARIF_LABELS[this.OPTARIF]
      : OPTARIF_LABELS["DEFAULT"];
    this.PTECLabel = this.PTEC && PTEC_LABELS[this.PTEC]
      ? PTEC_LABELS[this.PTEC]
      : PTEC_LABELS["DEFAULT"];
    this.PTECSeverity = this.PTEC && PTEC_SEVERITY[this.PTEC]
      ? PTEC_SEVERITY[this.PTEC]
      : PTEC_SEVERITY["DEFAULT"];

    this.otherData = {};
    for (const [key, value] of Object.entries(raw)) {
      if (!(TELEINFO_SPECIAL_KEYS as readonly string[]).includes(key)) {
        this.otherData[key] = value;
      }
    }
  }
}
