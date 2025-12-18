import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/useAuth';
import { useHeatingPlanHistory } from '../hooks/HeatingSchedulePage/useHeatingPlanHistory';
import fetchHeatingCalendar from '../services/fetchHeatingCalendar';
import SimpleDate from '../utils/simpleDate';
import HeatingCalendar from '../components/HeatingSchedulePage/Calendar/HeatingCalendar';
import RoomsSelector from '../components/HeatingSchedulePage/RoomsSelector/RoomsSelector';
import DateHeader from '../components/HeatingSchedulePage/DateHeader/DateHeader';
import Timeline from '../components/HeatingSchedulePage/Timeline/Timeline';
import TimelineSaveActions from '../components/HeatingSchedulePage/Timeline/TimelineSaveActions';
import DuplicationPanel from '../components/HeatingSchedulePage/Duplication/DuplicationPanel';
import styles from './HeatingSchedulePage.module.scss';
import duplicateHeatingPlan from '../services/duplicateHeatingPlan';

export default function HeatingSchedulePage() {
  const { user, accessToken, refresh } = useAuth();
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

  const handleSlotUpdate = (
    roomId,
    slotIndex,
    updatedSlot,
    resolvedSlots = null
  ) => {
    if (!dailyPlan) return;

    // Clone deep du dailyPlan
    const newPlan = {
      ...dailyPlan,
      rooms: dailyPlan.rooms.map((room) => {
        if (room.id === roomId) {
          // If we have resolvedSlots from overlap resolution, use them directly
          if (resolvedSlots !== null) {
            return { ...room, slots: resolvedSlots };
          }

          // Otherwise, handle simple operations (delete only)
          const newSlots = [...room.slots];

          if (updatedSlot === null) {
            // Delete slot
            newSlots.splice(slotIndex, 1);
          }

          return { ...room, slots: newSlots };
        }
        return room;
      }),
    };

    applyChange(newPlan);
  };

  const handleDuplicationApply = async (payload) => {
    if (!accessToken) {
      console.error('User not authenticated');
      return;
    }

    try {
      const result = await duplicateHeatingPlan(payload, accessToken, refresh);
      console.log('Duplication réussie:', result);

      // Rafraîchir le calendrier après duplication
      if (currentMonth) {
        const data = await fetchHeatingCalendar(
          currentMonth.year,
          currentMonth.month
        );
        setCalendar(data);
      }

      console.log(`${result['created/updated']} plans créés/mis à jour`);
    } catch (error) {
      console.error('Erreur lors de la duplication:', error);
      alert(`Erreur: ${error.message}`);
    }
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
          {user ? (
            <TimelineSaveActions
              onCancel={undo}
              onSave={save}
              canUndo={canUndo}
              hasChanges={hasChanges}
            />
          ) : (
            <p className={styles.loginMessage}>
              Vous devez être connecté pour modifier ces éléments
            </p>
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
        <DuplicationPanel
          sourceDate={selectedDate}
          selectedRooms={
            dailyPlan?.rooms.filter((r) => selectedRoomIds.includes(r.id)) || []
          }
          onApply={handleDuplicationApply}
          user={user}
        />
      </aside>
    </div>
  );
}
