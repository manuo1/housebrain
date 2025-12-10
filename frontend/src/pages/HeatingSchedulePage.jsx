import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/useAuth';
import fetchHeatingCalendar from '../services/fetchHeatingCalendar';
import fetchDailyHeatingPlan from '../services/fetchDailyHeatingPlan';
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
  const [dailyPlan, setDailyPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedRoomIds, setSelectedRoomIds] = useState([]);

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
          {user && <TimelineSaveActions />}
        </div>

        {loading ? (
          <div className={styles.timeline}>
            <p>Chargement...</p>
          </div>
        ) : (
          <Timeline
            rooms={dailyPlan?.rooms || []}
            selectedRoomIds={selectedRoomIds}
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
