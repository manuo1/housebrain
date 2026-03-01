import styles from "./SignalBars.module.scss";

interface SignalBarsProps {
  strength: number;
}

export default function SignalBars({ strength }: SignalBarsProps) {
  return (
    <div className={styles.signalBars}>
      {[1, 2, 3, 4, 5].map((bar) => (
        <div
          key={bar}
          className={`${styles.bar} ${bar <= strength ? styles.active : ""}`}
        />
      ))}
    </div>
  );
}
