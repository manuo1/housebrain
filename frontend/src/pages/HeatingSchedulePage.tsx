import { useState, useEffect } from "react";
import { useAuth } from "../contexts/useAuth";
import { useHeatingPlanHistory } from "../hooks/HeatingSchedulePage/useHeatingPlanHistory";
import fetchHeatingCalendar from "../services/fetchHeatingCalendar";
import SimpleDate from "../utils/simpleDate";
import HeatingCalendar from "../components/HeatingSchedulePage/Calendar/HeatingCalendar";
import RoomsSelector from "../components/HeatingSchedulePage/RoomsSelector/RoomsSelector";
import DateHeader from "../components/HeatingSchedulePage/DateHeader/DateHeader";
import Timeline from "../components/HeatingSchedulePage/Timeline/Timeline";
import TimelineSaveActions from "../components/HeatingSchedulePage/Timeline/TimelineSaveActions";
import DuplicationPanel, { DuplicationPayload } from "../components/HeatingSchedulePage/Duplication/DuplicationPanel";
import AiPlanInput from "../components/HeatingSchedulePage/AiPlanInput/AiPlanInput";
import styles from "./HeatingSchedulePage.module.scss";
import duplicateHeatingPlan from "../services/duplicateHeatingPlan";
import HeatingCalendarModel from "../models/HeatingCalendar";
import { Slot } from "../models/DailyHeatingPlan";
import DailyHeatingPlan, { RawDailyHeatingPlan } from "../models/DailyHeatingPlan";
import applyAiPlanModification from "../services/applyAiPlanModification";

interface CurrentMonth {
  year: number;
  month: number;
}

export default function HeatingSchedulePage() {
  const { user, accessToken, refresh } = useAuth();
  const [calendar, setCalendar] = useState<HeatingCalendarModel | null>(null);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [selectedDateObj, setSelectedDateObj] = useState<SimpleDate | null>(null);
  const [currentMonth, setCurrentMonth] = useState<CurrentMonth | null>(null);
  const [selectedRoomIds, setSelectedRoomIds] = useState<(number | null)[]>([]);
  const [pageError, setPageError] = useState<string | null>(null);

  const { dailyPlan, loading, canUndo, hasChanges, undo, save, applyChange } =
    useHeatingPlanHistory(selectedDate);

  // Fetch initial calendar
  useEffect(() => {
    async function loadInitialData() {
      try {
        const data = await fetchHeatingCalendar(undefined, undefined);
        setCalendar(data);
        if (data.today) {
          setSelectedDate(data.today.toISO());
          setSelectedDateObj(data.today);
          setCurrentMonth({ year: data.year!, month: data.month! });
        }
      } catch (error) {
        console.error("Error loading calendar:", error);
      }
    }
    loadInitialData();
  }, []);

  // Fetch calendar when month changes
  useEffect(() => {
    if (!currentMonth) return;
    async function loadCalendar() {
      try {
        const data = await fetchHeatingCalendar(currentMonth!.year, currentMonth!.month);
        setCalendar(data);
      } catch (error) {
        console.error("Error loading calendar:", error);
      }
    }
    loadCalendar();
  }, [currentMonth]);

  // Update selected rooms when dailyPlan changes
  useEffect(() => {
    if (dailyPlan?.rooms) {
      setSelectedRoomIds(dailyPlan.rooms.map((room) => room.id));
    }
  }, [dailyPlan]);

  const handleMonthChange = (year: number, month: number) => {
    setCurrentMonth({ year, month });
  };

  const handleDateSelect = (dateISO: string) => {
    setSelectedDate(dateISO);
    setSelectedDateObj(SimpleDate.fromISODate(dateISO));
  };

  const handleRoomSelectionChange = (roomIds: (number | null)[]) => {
    setSelectedRoomIds(roomIds);
  };

  const handleSlotUpdate = (
    roomId: number | null,
    slotIndex: number | null,
    updatedSlot: Slot | null,
    resolvedSlots: Slot[] | null = null
  ) => {
    if (!dailyPlan) return;

    // updatedSlot itself is never written into newSlots below: an actual
    // edit/creation always arrives with resolvedSlots already computed
    // (see Timeline.handleSlotSave). updatedSlot === null is only used
    // here as the deletion signal.
    const newRooms = dailyPlan.rooms.map((room) => {
      if (room.id !== roomId) return room;
      if (resolvedSlots !== null) return { ...room, slots: resolvedSlots };
      const newSlots = [...room.slots];
      if (updatedSlot === null && slotIndex !== null) {
        newSlots.splice(slotIndex, 1);
      }
      return { ...room, slots: newSlots };
    });

    // Rebuild through the constructor (rather than cloning dailyPlan's
    // rooms onto its prototype) so raw stays in sync with the edit. raw is
    // what gets sent to the AI endpoint (applyAiPlanModification) — if it
    // stayed stale, an AI request made after a manual edit would operate
    // on the plan as it was before that edit and could silently wipe it
    // out when the AI's response replaces the whole state.
    const newRaw: RawDailyHeatingPlan = {
      date: dailyPlan.date,
      rooms: newRooms.map((room) => ({
        room_id: room.id,
        name: room.name,
        slots: room.slots,
      })),
    };

    applyChange(new DailyHeatingPlan(newRaw));
  };

  const handleDuplicationApply = async (payload: DuplicationPayload) => {
    if (!accessToken) {
      console.error("User not authenticated");
      return;
    }
    setPageError(null);
    try {
      await duplicateHeatingPlan(payload, accessToken, refresh);
      if (currentMonth) {
        const data = await fetchHeatingCalendar(currentMonth.year, currentMonth.month);
        setCalendar(data);
      }
    } catch (error) {
      console.error("Erreur lors de la duplication:", error);
      setPageError((error as Error).message || "Erreur lors de la duplication.");
    }
  };

  const handleAiRequest = async (instruction: string) => {
    if (!dailyPlan || !accessToken) return;
    const newPlan = await applyAiPlanModification(
      { instruction, plan: dailyPlan.raw },
      accessToken,
      refresh
    );
    applyChange(newPlan);
  };

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
          <div className={styles.headerTop}>
            <DateHeader date={selectedDateObj} />
            {user ? (
              <TimelineSaveActions
                onCancel={undo}
                onSave={save}
                canUndo={canUndo}
                hasChanges={hasChanges}
                onError={setPageError}
              />
            ) : (
              <p className={styles.loginMessage}>
                Vous devez être connecté pour modifier ces éléments
              </p>
            )}
          </div>
          {pageError && <p className={styles.pageError}>{pageError}</p>}
          {user && (
            <AiPlanInput onSubmit={handleAiRequest} />
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
          selectedRooms={dailyPlan?.rooms.filter((r) => selectedRoomIds.includes(r.id)) || []}
          onApply={handleDuplicationApply}
          user={user}
        />
      </aside>
    </div>
  );
}
