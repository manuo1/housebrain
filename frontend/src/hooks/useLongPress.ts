import { useRef, useState, useCallback } from "react";

interface UseLongPressOptions {
  durationMs?: number;
  onComplete: () => void;
}

interface UseLongPressResult {
  pressing: boolean;
  progress: number; // 0 to 1
  secondsLeft: number;
  handlers: {
    onMouseDown: () => void;
    onMouseUp: () => void;
    onMouseLeave: () => void;
    onTouchStart: () => void;
    onTouchEnd: () => void;
    onTouchCancel: () => void;
  };
}

// Same start/stop logic driven by mouse (desktop) or touch (mobile) events.
export default function useLongPress({
  durationMs = 5000,
  onComplete,
}: UseLongPressOptions): UseLongPressResult {
  const [pressing, setPressing] = useState(false);
  const [progress, setProgress] = useState(0);
  const startTimeRef = useRef<number | null>(null);
  const frameRef = useRef<number | null>(null);

  const clear = useCallback(() => {
    if (frameRef.current !== null) {
      cancelAnimationFrame(frameRef.current);
      frameRef.current = null;
    }
    startTimeRef.current = null;
    setPressing(false);
    setProgress(0);
  }, []);

  const tick = useCallback(() => {
    if (startTimeRef.current === null) return;
    const elapsed = performance.now() - startTimeRef.current;
    const ratio = Math.min(elapsed / durationMs, 1);
    setProgress(ratio);

    if (ratio >= 1) {
      clear();
      onComplete();
      return;
    }
    frameRef.current = requestAnimationFrame(tick);
  }, [durationMs, onComplete, clear]);

  const start = useCallback(() => {
    startTimeRef.current = performance.now();
    setPressing(true);
    setProgress(0);
    frameRef.current = requestAnimationFrame(tick);
  }, [tick]);

  const cancel = useCallback(() => {
    clear();
  }, [clear]);

  const secondsLeft = Math.max(0, Math.ceil((durationMs / 1000) * (1 - progress)));

  return {
    pressing,
    progress,
    secondsLeft,
    handlers: {
      onMouseDown: start,
      onMouseUp: cancel,
      onMouseLeave: cancel,
      onTouchStart: start,
      onTouchEnd: cancel,
      onTouchCancel: cancel,
    },
  };
}
