export const timeToMinutes = (timeStr: string): number => {
  const [hours, minutes] = timeStr.split(":").map(Number);
  return hours * 60 + minutes;
};

export const minutesToTime = (minutes: number): string => {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${String(hours).padStart(2, "0")}:${String(mins).padStart(2, "0")}`;
};

export const timeToPercent = (timeStr: string): number => {
  const [hours, minutes] = timeStr.split(":").map(Number);
  const totalMinutes = hours * 60 + minutes;
  return (totalMinutes / 1440) * 100; // 1440 = 24h * 60min
};

export const percentToTime = (percent: number): string => {
  const totalMinutes = Math.round((percent / 100) * 1440);
  return minutesToTime(totalMinutes);
};

interface SlotPosition {
  left: string;
  width: string;
}

export const calculateSlotPosition = (slot: { start: string; end: string }): SlotPosition => {
  const startPercent = timeToPercent(slot.start);
  const endPercent = timeToPercent(slot.end);
  const widthPercent = endPercent - startPercent;

  return {
    left: `${startPercent}%`,
    width: `${widthPercent}%`,
  };
};
