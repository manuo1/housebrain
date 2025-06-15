import TeleinfoData from "../models/TeleinfoData";

const rawMockData = {
  ADCO: "022061465334",
  OPTARIF: "HC..",
  ISOUSC: "45",
  HCHC: "004987808",
  HCHP: "000259088",
  PTEC: "HP..",
  IINST: "002",
  IMAX: "090",
  PAPP: "00640",
  HHPHC: "A",
  MOTDETAT: "000000",
  last_read: "2025-06-15T16:52:16Z",
};

const mockTeleinfoData = new TeleinfoData(rawMockData);

export default mockTeleinfoData;
