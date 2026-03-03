import { formatDate, getWeekRange } from "./utils/duplicationDateUtils";
import styles from "./DuplicationSummary.module.scss";
import { PlanRoom } from "../../../models/DailyHeatingPlan";

type DuplicationMode = "day" | "week";

const WEEKDAY_LABELS: Record<string, string> = {
  monday: "lundis", tuesday: "mardis", wednesday: "mercredis",
  thursday: "jeudis", friday: "vendredis", saturday: "samedis", sunday: "dimanches",
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
  const getWeekdaysList = () => selectedWeekdays.map((day) => WEEKDAY_LABELS[day]).join(", ");

  return (
    <div className={styles.summary}>
      <div className={styles.content}>
        <div className={styles.section}>
          {mode !== "week" ? (
            <>Le planning du :<br />{formatDate(sourceDate)}<br />des pièces :</>
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
            {mode === "week" ? (<>Depuis la semaine du :<br />{startWeekRange?.mondayText} au {startWeekRange?.sundayText}</>) : (<>Depuis le :<br />{formatDate(startDate)}</>)}
          </div>
        )}
        {endDate && (
          <div className={styles.section}>
            {mode === "week" ? (<>Jusqu'à la semaine du :<br />{endWeekRange?.mondayText} au {endWeekRange?.sundayText}</>) : (<>Jusqu'au :<br />{formatDate(endDate)}</>)}
          </div>
        )}
      </div>
    </div>
  );
}
