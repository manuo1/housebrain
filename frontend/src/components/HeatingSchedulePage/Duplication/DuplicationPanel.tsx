import { useState, useEffect } from "react";
import DuplicationModeToggle from "./DuplicationModeToggle";
import WeekdaySelector from "./WeekdaySelector";
import DuplicationDate from "./DuplicationDate";
import DuplicationSummary from "./DuplicationSummary";
import DuplicationApplyButton from "./DuplicationApplyButton";
import ConfirmModal from "../../common/ConfirmModal";
import { addDays, getNextMonday, getMondayOfWeek, getSundayOfWeek } from "./utils/duplicationDateUtils";
import { getValidationErrors } from "./utils/duplicationValidation";
import styles from "./DuplicationPanel.module.scss";
import { PlanRoom } from "../../../models/DailyHeatingPlan";
import { User } from "../../../contexts/AuthContext";

type DuplicationMode = "day" | "week";

export interface DuplicationPayload {
  type: DuplicationMode;
  source_date: string;
  repeat_since: string;
  repeat_until: string;
  room_ids: (number | null)[];
  weekdays?: string[];
}

interface DuplicationPanelProps {
  sourceDate: string;
  selectedRooms: PlanRoom[];
  onApply: (payload: DuplicationPayload) => void;
  user: User | null;
}

export default function DuplicationPanel({ sourceDate, selectedRooms, onApply, user }: DuplicationPanelProps) {
  const [mode, setMode] = useState<DuplicationMode>("day");
  const [selectedWeekdays, setSelectedWeekdays] = useState<string[]>([]);
  const [startDate, setStartDate] = useState<string>("");
  const [endDate, setEndDate] = useState<string>("");
  const [showConfirmModal, setShowConfirmModal] = useState<boolean>(false);

  const startDateMin = mode === "week" ? getNextMonday(sourceDate) : addDays(sourceDate, 1);
  const endDateMin = startDate ? (mode === "week" ? getSundayOfWeek(startDate) : addDays(startDate, 1)) : "";
  const endDateMax = startDate ? addDays(startDate, 365) : "";

  useEffect(() => {
    if (sourceDate) {
      setStartDate(mode === "week" ? getNextMonday(sourceDate) : addDays(sourceDate, 1));
    }
  }, [sourceDate, mode]);

  const handleStartDateChange = (newDate: string) => {
    setStartDate(mode === "week" && newDate ? getMondayOfWeek(newDate) : newDate);
  };

  const handleEndDateChange = (newDate: string) => {
    setEndDate(mode === "week" && newDate ? getSundayOfWeek(newDate) : newDate);
  };

  const handleConfirm = () => {
    const payload: DuplicationPayload = {
      type: mode,
      source_date: sourceDate,
      repeat_since: startDate,
      repeat_until: endDate,
      room_ids: selectedRooms.map((r) => r.id),
    };
    if (mode === "day") payload.weekdays = selectedWeekdays;
    onApply(payload);
  };

  const validationErrors = getValidationErrors({ mode, selectedRooms, sourceDate, startDate, endDate, selectedWeekdays });
  const isValid = validationErrors.length === 0;

  return (
    <div className={styles.duplicationPanel}>
      <h3>Options de duplication</h3>
      <div className={styles.section}>
        <DuplicationModeToggle mode={mode} onChange={setMode} />
      </div>
      {mode === "day" && (
        <div className={styles.section}>
          <WeekdaySelector selectedDays={selectedWeekdays} onChange={setSelectedWeekdays} />
        </div>
      )}
      <div className={styles.dateRow}>
        <DuplicationDate label="Date de début" value={startDate} onChange={handleStartDateChange} min={startDateMin} />
        <DuplicationDate label="Date de fin" value={endDate} onChange={handleEndDateChange} min={endDateMin} max={endDateMax} />
      </div>
      {validationErrors.length > 0 && (
        <div className={styles.errors}>
          <ul>{validationErrors.map((error, index) => <li key={index}>{error}</li>)}</ul>
        </div>
      )}
      <div className={styles.section}>
        <DuplicationSummary mode={mode} sourceDate={sourceDate} startDate={startDate} endDate={endDate} selectedRooms={selectedRooms} selectedWeekdays={selectedWeekdays} />
      </div>
      {user && <DuplicationApplyButton onClick={() => setShowConfirmModal(true)} disabled={!isValid} />}
      <ConfirmModal
        isOpen={showConfirmModal}
        onClose={() => setShowConfirmModal(false)}
        onConfirm={handleConfirm}
        title="Confirmer la duplication"
        message="Cette action écrasera les plannings existants sur les dates sélectionnées. Voulez-vous continuer ?"
        confirmText="Dupliquer"
        cancelText="Annuler"
        confirmVariant="danger"
      />
    </div>
  );
}
