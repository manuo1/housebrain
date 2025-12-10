import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/useAuth';
import { useHeatingPlanHistory } from '../hooks/HeatingSchedulePage/useHeatingPlanHistory';
import fetchHeatingCalendar from '../services/fetchHeatingCalendar';
import SimpleDate from '../utils/simpleDate';
import HeatingCalendar from '../components/HeatingSchedulePage/HeatingCalendar';
import RoomsSelector from '../components/HeatingSchedulePage/RoomsSelector';
import DateHeader from '../components/HeatingSchedulePage/DateHeader';
import Timeline from '../components/HeatingSchedulePage/Timeline';
import TimelineSaveActions from '../components/HeatingSchedulePage/TimelineSaveActions';
import styles from './HeatingSchedulePage.module.scss';

export default function HeatingSchedulePage() {
  const { user } = useAuth();
  const [calendar, setCalendar] = useState(null);
  const [selectedDate, setSelectedDate] = useState(null);
  const [selectedDateObj, setSelectedDateObj] = useState(null);
  const [currentMonth, setCurrentMonth] = useState(null);
  const [selectedRoomIds, setSelectedRoomIds] = useState([]);

  const { dailyPlan, loading, canUndo, hasChanges, undo, save, applyChange } =
    useHeatingPlanHistory(selectedDate);

  // Fetch initial calendar
  useEffect(() => {
    async function loadInitialData() {
      try {
        const data = await fetchHeatingCalendar(null, null);
        setCalendar(data);

        if (data.today) {
          setSelectedDate(data.today.toISO());
          setSelectedDateObj(data.today);
          setCurrentMonth({ year: data.year, month: data.month });
        }
      } catch (error) {
        console.error('Error loading calendar:', error);
      }
    }
    loadInitialData();
  }, []);

  // Fetch calendar when month changes
  useEffect(() => {
    if (!currentMonth) return;

    async function loadCalendar() {
      try {
        const data = await fetchHeatingCalendar(
          currentMonth.year,
          currentMonth.month
        );
        setCalendar(data);
      } catch (error) {
        console.error('Error loading calendar:', error);
      }
    }
    loadCalendar();
  }, [currentMonth]);

  // Update selected rooms when dailyPlan changes
  useEffect(() => {
    if (dailyPlan && dailyPlan.rooms) {
      setSelectedRoomIds(dailyPlan.rooms.map((room) => room.id));
    }
  }, [dailyPlan]);

  const handleMonthChange = (year, month) => {
    setCurrentMonth({ year, month });
  };

  const handleDateSelect = (dateISO) => {
    setSelectedDate(dateISO);
    setSelectedDateObj(SimpleDate.fromISODate(dateISO));
  };

  const handleRoomSelectionChange = (roomIds) => {
    setSelectedRoomIds(roomIds);
  };

  const handleSlotUpdate = (roomId, slotIndex, updatedSlot) => {
    if (!dailyPlan) return;

    // Clone deep du dailyPlan
    const newPlan = {
      ...dailyPlan,
      rooms: dailyPlan.rooms.map((room) => {
        if (room.id === roomId) {
          const newSlots = [...room.slots];

          if (updatedSlot === null) {
            // Delete slot
            newSlots.splice(slotIndex, 1);
          } else if (slotIndex === -1) {
            // Create new slot
            newSlots.push(updatedSlot);
            // Sort slots by start time
            newSlots.sort((a, b) => {
              const [aH, aM] = a.start.split(':').map(Number);
              const [bH, bM] = b.start.split(':').map(Number);
              return aH * 60 + aM - (bH * 60 + bM);
            });
          } else {
            // Update slot
            newSlots[slotIndex] = updatedSlot;
          }

          return { ...room, slots: newSlots };
        }
        return room;
      }),
    };

    applyChange(newPlan);
  };

  // Show loader while initial data is loading
  if (!calendar || !selectedDate) {
    return (
      <div className={styles.loading}>
        <p>Chargement...</p>
      </div>
    );
  }

  return (
    <div className={styles.heatingSchedulePage}>
      <aside className={styles.sidebar}>
        <HeatingCalendar
          calendar={calendar}
          selectedDate={selectedDate}
          onDateSelect={handleDateSelect}
          onMonthChange={handleMonthChange}
        />

        <RoomsSelector
          rooms={dailyPlan?.rooms || []}
          selectedRoomIds={selectedRoomIds}
          onSelectionChange={handleRoomSelectionChange}
        />
      </aside>

      <main className={styles.mainContent}>
        <div className={styles.header}>
          <DateHeader date={selectedDateObj} />
          {user && (
            <TimelineSaveActions
              onCancel={undo}
              onSave={save}
              canUndo={canUndo}
              hasChanges={hasChanges}
            />
          )}
        </div>

        {loading ? (
          <div className={styles.timeline}>
            <p>Chargement...</p>
          </div>
        ) : (
          <Timeline
            rooms={dailyPlan?.rooms || []}
            selectedRoomIds={selectedRoomIds}
            onSlotUpdate={handleSlotUpdate}
            user={user}
          />
        )}
      </main>

      <aside className={styles.rightPanel}>
        <h3>Options de duplication (TODO)</h3>
        <p>Répéter les jours, date de fin, etc.</p>
      </aside>
    </div>
  );
}
