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

  const getValidationErrors = () => {
    const errors = [];

    // 1. Rooms vides
    if (selectedRooms.length === 0) {
      errors.push('Aucune pièce sélectionnée');
    }

    // 2. EndDate manquante
    if (!endDate) {
      errors.push('Veuillez sélectionner une date de fin');
    }

    // 3. Weekdays vides en mode day
    if (mode === 'day' && selectedWeekdays.length === 0) {
      errors.push('Veuillez sélectionner au moins un jour de la semaine');
    }

    // 4 & 5. Comparaison dates
    if (sourceDate && endDate) {
      const source = new Date(sourceDate);
      const end = new Date(endDate);
      const diffDays = Math.floor((end - source) / (1000 * 60 * 60 * 24));

      // sourceDate >= endDate
      if (diffDays < 1) {
        errors.push('La date de fin doit être au moins le lendemain');
      }

      // Mode week : vérifier semaine différente
      if (mode === 'week' && diffDays < 7) {
        errors.push('La date de fin doit être au moins la semaine suivante');
      }

      // Max 365 jours
      if (diffDays > 365) {
        errors.push('La période ne peut pas dépasser 365 jours');
      }
    }

    return errors;
  };

  const handleApply = () => {
    // TODO: Remplacer par un modal custom plus joli
    const confirmed = window.confirm(
      'Attention : Cette action écrasera les plannings existants sur les dates sélectionnées. Voulez-vous continuer ?'
    );

    if (!confirmed) return;

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

  const validationErrors = getValidationErrors();
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

      <div className={styles.section}>
        <DuplicationEndDate value={endDate} onChange={setEndDate} />
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
          endDate={endDate}
          selectedRooms={selectedRooms}
          selectedWeekdays={selectedWeekdays}
        />
      </div>

      <DuplicationApplyButton onClick={handleApply} disabled={!isValid} />
    </div>
  );
}
