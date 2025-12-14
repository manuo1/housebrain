import React, { useState, useEffect } from 'react';
import DuplicationModeToggle from './DuplicationModeToggle';
import WeekdaySelector from './WeekdaySelector';
import DuplicationDate from './DuplicationDate';
import DuplicationSummary from './DuplicationSummary';
import DuplicationApplyButton from './DuplicationApplyButton';
import ConfirmModal from '../../common/ConfirmModal';
import {
  addDays,
  getNextMonday,
  getMondayOfWeek,
  getSundayOfWeek,
} from './duplicationDateUtils';
import { getValidationErrors } from './duplicationValidation';
import styles from './DuplicationPanel.module.scss';

export default function DuplicationPanel({
  sourceDate,
  selectedRooms,
  onApply,
  user,
}) {
  const [mode, setMode] = useState('day');
  const [selectedWeekdays, setSelectedWeekdays] = useState([]);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [showConfirmModal, setShowConfirmModal] = useState(false);

  // Calcul des min/max
  const startDateMin =
    mode === 'week' ? getNextMonday(sourceDate) : addDays(sourceDate, 1);
  const endDateMin = startDate
    ? mode === 'week'
      ? getSundayOfWeek(startDate)
      : addDays(startDate, 1)
    : '';
  const endDateMax = startDate ? addDays(startDate, 365) : '';

  // Pré-remplir startDate quand sourceDate ou mode change
  useEffect(() => {
    if (sourceDate) {
      const min =
        mode === 'week' ? getNextMonday(sourceDate) : addDays(sourceDate, 1);
      setStartDate(min);
    }
  }, [sourceDate, mode]);

  // Handler pour startDate : ajuster au lundi en mode week
  const handleStartDateChange = (newDate) => {
    if (mode === 'week' && newDate) {
      const adjustedDate = getMondayOfWeek(newDate);
      setStartDate(adjustedDate);
    } else {
      setStartDate(newDate);
    }
  };

  // Handler pour endDate : ajuster au dimanche en mode week
  const handleEndDateChange = (newDate) => {
    if (mode === 'week' && newDate) {
      const adjustedDate = getSundayOfWeek(newDate);
      setEndDate(adjustedDate);
    } else {
      setEndDate(newDate);
    }
  };

  const handleApplyClick = () => {
    setShowConfirmModal(true);
  };

  const handleConfirm = () => {
    const payload = {
      type: mode,
      source_date: sourceDate,
      repeat_since: startDate,
      repeat_until: endDate,
      room_ids: selectedRooms.map((r) => r.id),
    };
    if (mode === 'day') {
      payload.weekdays = selectedWeekdays;
    }
    onApply(payload);
  };

  const validationErrors = getValidationErrors({
    mode,
    selectedRooms,
    sourceDate,
    startDate,
    endDate,
    selectedWeekdays,
  });
  const isValid = validationErrors.length === 0;

  return (
    <div className={styles.duplicationPanel}>
      <h3>Options de duplication</h3>
      <div className={styles.section}>
        <DuplicationModeToggle mode={mode} onChange={setMode} />
      </div>
      {mode === 'day' && (
        <div className={styles.section}>
          <WeekdaySelector
            selectedDays={selectedWeekdays}
            onChange={setSelectedWeekdays}
          />
        </div>
      )}
      <div className={styles.dateRow}>
        <DuplicationDate
          label="Date de début"
          value={startDate}
          onChange={handleStartDateChange}
          min={startDateMin}
        />
        <DuplicationDate
          label="Date de fin"
          value={endDate}
          onChange={handleEndDateChange}
          min={endDateMin}
          max={endDateMax}
        />
      </div>
      {validationErrors.length > 0 && (
        <div className={styles.errors}>
          <ul>
            {validationErrors.map((error, index) => (
              <li key={index}>{error}</li>
            ))}
          </ul>
        </div>
      )}
      <div className={styles.section}>
        <DuplicationSummary
          mode={mode}
          sourceDate={sourceDate}
          startDate={startDate}
          endDate={endDate}
          selectedRooms={selectedRooms}
          selectedWeekdays={selectedWeekdays}
        />
      </div>
      {user && (
        <DuplicationApplyButton
          onClick={handleApplyClick}
          disabled={!isValid}
        />
      )}
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
