import styles from "./LongPressCountdown.module.scss";

interface LongPressCountdownProps {
  progress: number; // 0 to 1
  secondsLeft: number;
  compact?: boolean;
}

const RADIUS = 26;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

export default function LongPressCountdown({ progress, secondsLeft, compact }: LongPressCountdownProps) {
  const offset = CIRCUMFERENCE * (1 - progress);

  return (
    <div className={`${styles.countdown} ${compact ? styles.compact : ""}`}>
      <svg viewBox="0 0 60 60" className={styles.ring}>
        <circle className={styles.track} cx="30" cy="30" r={RADIUS} />
        <circle
          className={styles.progress}
          cx="30"
          cy="30"
          r={RADIUS}
          strokeDasharray={CIRCUMFERENCE}
          strokeDashoffset={offset}
        />
      </svg>
      <span className={styles.value}>{secondsLeft}</span>
    </div>
  );
}
