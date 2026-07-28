import { TELEINFO_LABELS } from "../../constants/teleinfoConstants";
import styles from "./TeleinfoTable.module.scss";
import { formatValue, formatOtherData } from "../../utils/teleinfoUtils";
import TeleinfoData from "../../models/TeleinfoData";

interface TeleinfoTableProps {
  data: TeleinfoData;
}

export default function TeleinfoTable({ data }: TeleinfoTableProps) {
  // Les clés ci-dessous doivent rester alignées avec TELEINFO_SPECIAL_KEYS
  // (constants/teleinfoConstants.ts), qui les exclut de otherData côté TeleinfoData.
  const toDisplay: Record<string, string> = {
    [TELEINFO_LABELS.OPTARIF]: data.OPTARIFLabel,
    [TELEINFO_LABELS.ISOUSC]: formatValue("ISOUSC", data.ISOUSC),
    [TELEINFO_LABELS.PTEC]: data.PTECLabel,
    [TELEINFO_LABELS.IINST]: formatValue("IINST", data.IINST),
    [TELEINFO_LABELS.IMAX]: formatValue("IMAX", data.IMAX),
    [TELEINFO_LABELS.PAPP]: formatValue("PAPP", data.PAPP),
    "Dernier relevé": data.last_read ?? "N/A",
    ...formatOtherData(data.otherData),
  };

  return (
    <table className={styles.table}>
      <thead>
        <tr>
          <th scope="col">Label</th>
          <th scope="col">Valeur</th>
        </tr>
      </thead>
      <tbody>
        {Object.entries(toDisplay).map(([label, value]) => (
          <tr key={label}>
            <td>{label}</td>
            <td>{value ?? "N/A"}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
