import React, { useState } from 'react';
import DuplicationModeToggle from './DuplicationModeToggle';
import WeekdaySelector from './WeekdaySelector';
import DuplicationEndDate from './DuplicationEndDate';
import DuplicationSummary from './DuplicationSummary';
import DuplicationApplyButton from './DuplicationApplyButton';
import styles from './DuplicationPanel.module.scss';

export default function DuplicationPanel({
  sourceDate,
  selectedRooms,
  onApply,
}) {
  const [mode, setMode] = useState('day');
  const [selectedWeekdays, setSelectedWeekdays] = useState([]);
  const [endDate, setEndDate] = useState('');

  const handleApply = () => {
    const payload = {
      type: mode,
      source_date: sourceDate,
      repeat_until: endDate,
      room_ids: selectedRooms.map((r) => r.id),
    };

    if (mode === 'day') {
      payload.weekdays = selectedWeekdays;
    }

    onApply(payload);
  };

  const isValid = () => {
    if (!endDate) return false;
    if (selectedRooms.length === 0) return false;
    if (mode === 'day' && selectedWeekdays.length === 0) return false;
    return true;
  };

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

      <div className={styles.section}>
        <DuplicationEndDate value={endDate} onChange={setEndDate} />
      </div>

      <div className={styles.section}>
        <DuplicationSummary
          mode={mode}
          sourceDate={sourceDate}
          endDate={endDate}
          selectedRooms={selectedRooms}
          selectedWeekdays={selectedWeekdays}
        />
      </div>

      <DuplicationApplyButton onClick={handleApply} disabled={!isValid()} />
    </div>
  );
}
