import { useState, useEffect } from "react";
import { useAuth } from "../contexts/useAuth";
import { useEquipmentPlanHistory } from "../hooks/EquipmentSchedulePage/useEquipmentPlanHistory";
import fetchEquipmentCalendar from "../services/fetchEquipmentCalendar";
import SimpleDate from "../utils/simpleDate";
import EquipmentCalendar from "../components/EquipmentSchedulePage/Calendar/EquipmentCalendar";
import DateHeader from "../components/EquipmentSchedulePage/DateHeader/DateHeader";
import Timeline from "../components/EquipmentSchedulePage/Timeline/Timeline";
import TimelineSaveActions from "../components/EquipmentSchedulePage/Timeline/TimelineSaveActions";
import AiPlanInput from "../components/EquipmentSchedulePage/AiPlanInput/AiPlanInput";
import DuplicationChat, { PropagationSeed } from "../components/EquipmentSchedulePage/DuplicationChat/DuplicationChat";
import styles from "./EquipmentSchedulePage.module.scss";
import EquipmentCalendarModel from "../models/EquipmentCalendar";
import { Slot } from "../models/DailyEquipmentPlan";
import DailyEquipmentPlan, { RawDailyEquipmentPlan } from "../models/DailyEquipmentPlan";
import applyAiEquipmentPlanModification from "../services/applyAiEquipmentPlanModification";

interface CurrentMonth {
  year: number;
  month: number;
}

export default function EquipmentSchedulePage() {
  const { user, accessToken, refresh } = useAuth();
  const [calendar, setCalendar] = useState<EquipmentCalendarModel | null>(null);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [selectedDateObj, setSelectedDateObj] = useState<SimpleDate | null>(null);
  const [currentMonth, setCurrentMonth] = useState<CurrentMonth | null>(null);
  const [pageError, setPageError] = useState<string | null>(null);
  const [propagationSeed, setPropagationSeed] = useState<PropagationSeed | null>(null);

  const { dailyPlan, loading, canUndo, hasChanges, undo, save, applyChange } =
    useEquipmentPlanHistory(selectedDate);

  // Fetch initial calendar
  useEffect(() => {
    async function loadInitialData() {
      try {
        const data = await fetchEquipmentCalendar(undefined, undefined);
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
        const data = await fetchEquipmentCalendar(currentMonth!.year, currentMonth!.month);
        setCalendar(data);
      } catch (error) {
        console.error("Error loading calendar:", error);
      }
    }
    loadCalendar();
  }, [currentMonth]);

  const handleMonthChange = (year: number, month: number) => {
    setCurrentMonth({ year, month });
  };

  const handleDateSelect = (dateISO: string) => {
    setSelectedDate(dateISO);
    setSelectedDateObj(SimpleDate.fromISODate(dateISO));
  };

  const handleSlotUpdate = (
    equipmentType: string,
    equipmentId: number | null,
    slotIndex: number | null,
    updatedSlot: Slot | null,
    resolvedSlots: Slot[] | null = null
  ) => {
    if (!dailyPlan) return;

    // updatedSlot itself is never written into newSlots below: an actual
    // edit/creation always arrives with resolvedSlots already computed
    // (see Timeline.handleSlotSave). updatedSlot === null is only used
    // here as the deletion signal.
    const newEquipments = dailyPlan.equipments.map((equipment) => {
      if (equipment.type !== equipmentType || equipment.id !== equipmentId) return equipment;
      if (resolvedSlots !== null) return { ...equipment, slots: resolvedSlots };
      const newSlots = [...equipment.slots];
      if (updatedSlot === null && slotIndex !== null) {
        newSlots.splice(slotIndex, 1);
      }
      return { ...equipment, slots: newSlots };
    });

    const newRaw: RawDailyEquipmentPlan = {
      date: dailyPlan.date,
      equipments: newEquipments.map((equipment) => ({
        type: equipment.type,
        id: equipment.id,
        name: equipment.name,
        slots: equipment.slots,
      })),
    };

    applyChange(new DailyEquipmentPlan(newRaw));
  };

  const handleAiRequest = async (instruction: string) => {
    if (!dailyPlan || !accessToken) return;
    const newPlan = await applyAiEquipmentPlanModification(
      { instruction, plan: dailyPlan.raw },
      accessToken,
      refresh
    );
    applyChange(newPlan);
  };

  // Nothing to refresh: the equipment calendar carries no per-day status, and the
  // displayed day is the duplication source, which a duplication never changes.
  const handleDuplicationSuccess = () => {
    return;
  };

  const handleSave = async () => {
    const changedEquipments = await save();
    if (changedEquipments.length > 0) {
      setPropagationSeed({ equipments: changedEquipments, nonce: Date.now() });
    }
  };

  if (!calendar || !selectedDate) {
    return (
      <div className={styles.loading}>
        <p>Chargement...</p>
      </div>
    );
  }

  return (
    <div className={styles.equipmentSchedulePage}>
      <aside className={styles.sidebar}>
        <EquipmentCalendar
          calendar={calendar}
          selectedDate={selectedDate}
          onDateSelect={handleDateSelect}
          onMonthChange={handleMonthChange}
        />
      </aside>

      <main className={styles.mainContent}>
        <div className={styles.header}>
          <div className={styles.headerTop}>
            <DateHeader date={selectedDateObj} />
            {user ? (
              <TimelineSaveActions
                onCancel={undo}
                onSave={handleSave}
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
            equipments={dailyPlan?.equipments || []}
            onSlotUpdate={handleSlotUpdate}
            user={user}
          />
        )}
      </main>

      {user && selectedDate && (
        <div className={styles.rightPanel}>
          <DuplicationChat
            sourceDate={selectedDate}
            onDuplicationSuccess={handleDuplicationSuccess}
            propagationSeed={propagationSeed}
          />
        </div>
      )}
    </div>
  );
}
