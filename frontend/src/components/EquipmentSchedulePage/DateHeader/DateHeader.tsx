import { formatFullDayLabel } from "../../../utils/dateUtils";
import styles from "./DateHeader.module.scss";
import SimpleDate from "../../../utils/simpleDate";

interface DateHeaderProps {
  date: SimpleDate | null | undefined;
}

export default function DateHeader({ date }: DateHeaderProps) {
  return <h2 className={styles.dateHeader}>{formatFullDayLabel(date)}</h2>;
}
