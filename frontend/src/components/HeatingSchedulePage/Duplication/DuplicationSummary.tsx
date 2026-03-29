import { formatDateDD_MM_YYYY, getWeekRange, getDayLabel } from "../../../utils/dateUtils";
import styles from "./DuplicationSummary.module.scss";
import { PlanRoom } from "../../../models/DailyHeatingPlan";

type DuplicationMode = "day" | "week";

const WEEKDAY_ISO: Record<string, number> = {
  monday: 1, tuesday: 2, wednesday: 3,
  thursday: 4, friday: 5, saturday: 6, sunday: 7,
};

interface DuplicationSummaryProps {
  mode: DuplicationMode;
  sourceDate: string;
  startDate: string;
  endDate: string;
  selectedRooms: PlanRoom[];
  selectedWeekdays: string[];
}

export default function DuplicationSummary({ mode, sourceDate, startDate, endDate, selectedRooms, selectedWeekdays }: DuplicationSummaryProps) {
  const sourceWeekRange = mode === "week" ? getWeekRange(sourceDate) : null;
  const startWeekRange = mode === "week" && startDate ? getWeekRange(startDate) : null;
  const endWeekRange = mode === "week" && endDate ? getWeekRange(endDate) : null;

  const getWeekdaysList = () =>
    selectedWeekdays.map((day) => getDayLabel(WEEKDAY_ISO[day]).toLowerCase() + "s").join(", ");

  return (
    <div className={styles.summary}>
      <div className={styles.content}>
        <div className={styles.section}>
          {mode !== "week" ? (
            <>Le planning du :<br />{formatDateDD_MM_YYYY(sourceDate)}<br />des pièces :</>
          ) : (
            <>Les planning de la semaine du :<br />{sourceWeekRange?.mondayText} au {sourceWeekRange?.sundayText}<br />des pièces :</>
          )}
        </div>
        <div className={styles.list}>
          {selectedRooms.map((room) => (
            <div key={room.id} className={styles.item}>• {room.name}</div>
          ))}
        </div>
        {mode === "day" && selectedWeekdays.length > 0 && (
          <>
            <div className={styles.section}>Sera dupliqué tous les :</div>
            <div className={styles.list}><div className={styles.item}>• {getWeekdaysList()}</div></div>
          </>
        )}
        {mode === "week" && <div className={styles.section}>Seront dupliqués chaque semaine</div>}
        {startDate && (
          <div className={styles.section}>
            {mode === "week" ? (<>Depuis la semaine du :<br />{startWeekRange?.mondayText} au {startWeekRange?.sundayText}</>) : (<>Depuis le :<br />{formatDateDD_MM_YYYY(startDate)}</>)}
          </div>
        )}
        {endDate && (
          <div className={styles.section}>
            {mode === "week" ? (<>Jusqu'à la semaine du :<br />{endWeekRange?.mondayText} au {endWeekRange?.sundayText}</>) : (<>Jusqu'au :<br />{formatDateDD_MM_YYYY(endDate)}</>)}
          </div>
        )}
      </div>
    </div>
  );
}
