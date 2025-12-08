import React, { useState, useEffect } from 'react';
import fetchHeatingCalendar from '../services/fetchHeatingCalendar';
import fetchDailyHeatingPlan from '../services/fetchDailyHeatingPlan';
import HeatingCalendar from '../components/HeatingSchedulePage/HeatingCalendar';
import RoomsSelector from '../components/HeatingSchedulePage/RoomsSelector';
import DateHeader from '../components/HeatingSchedulePage/DateHeader';
import SimpleDate from '../utils/simpleDate';
import styles from './HeatingSchedulePage.module.scss';

export default function HeatingSchedulePage() {
  const [calendar, setCalendar] = useState(null);
  const [selectedDate, setSelectedDate] = useState(null); // ISO string
  const [selectedDateObj, setSelectedDateObj] = useState(null); // SimpleDate
  const [currentMonth, setCurrentMonth] = useState(null);
  const [dailyPlan, setDailyPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedRoomIds, setSelectedRoomIds] = useState([]);

  // Fetch initial calendar (backend provides today and current month)
  useEffect(() => {
    async function loadInitialData() {
      try {
        // Fetch calendar without params - backend returns current month by default
        // Or pass null/0 to indicate "give me current month"
        const data = await fetchHeatingCalendar(null, null);
        setCalendar(data);

        // Set today as selected date
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

  // Fetch daily plan when date changes
  useEffect(() => {
    if (!selectedDate) return;

    async function loadDailyPlan() {
      setLoading(true);
      try {
        const data = await fetchDailyHeatingPlan(selectedDate);
        setDailyPlan(data);

        if (data && data.rooms) {
          setSelectedRoomIds(data.rooms.map((room) => room.id));
        }
      } catch (error) {
        console.error('Error loading daily plan:', error);
      } finally {
        setLoading(false);
      }
    }
    loadDailyPlan();
  }, [selectedDate]);

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
          <div className={styles.actions}>
            <button className={styles.btnSecondary}>Annuler</button>
            <button className={styles.btnPrimary}>Enregistrer</button>
          </div>
        </div>

        <div className={styles.timeline}>
          {loading ? (
            <p>Chargement...</p>
          ) : (
            <>
              <h3>⏰ Timeline (TODO)</h3>
              <p>Pièces sélectionnées : {selectedRoomIds.length}</p>
              {dailyPlan && <pre>{JSON.stringify(dailyPlan, null, 2)}</pre>}
            </>
          )}
        </div>
      </main>

      <aside className={styles.rightPanel}>
        <h3>⚙️ Options de duplication (TODO)</h3>
        <p>Répéter les jours, date de fin, etc.</p>
      </aside>
    </div>
  );
}
