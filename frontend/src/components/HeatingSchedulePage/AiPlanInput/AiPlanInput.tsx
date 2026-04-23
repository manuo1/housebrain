import { useState, useRef, useEffect } from "react";
import styles from "./AiPlanInput.module.scss";

interface AiPlanInputProps {
  onSubmit: (instruction: string) => Promise<void>;
  disabled?: boolean;
}

export default function AiPlanInput({ onSubmit, disabled }: AiPlanInputProps) {
  const [expanded, setExpanded] = useState(false);
  const [instruction, setInstruction] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (expanded && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [expanded]);

  const handleToggle = () => {
    if (expanded) {
      setExpanded(false);
      setInstruction("");
      setError(null);
    } else {
      setExpanded(true);
    }
  };

  const handleSubmit = async () => {
    if (!instruction.trim() || loading) return;
    setLoading(true);
    setError(null);
    try {
      await onSubmit(instruction.trim());
      // Succès : on ferme et on vide
      setInstruction("");
      setExpanded(false);
    } catch (err) {
      setError((err as Error).message || "Impossible de générer les modifications.");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
    if (e.key === "Escape") {
      setExpanded(false);
      setInstruction("");
      setError(null);
    }
  };

  const btnLabel = loading ? "Réflexion..." : "Appliquer";

  return (
    <div className={styles.wrapper}>
      <button
        className={`${styles.toggleBtn} ${expanded ? styles.active : ""}`}
        onClick={handleToggle}
        disabled={disabled}
        type="button"
      >
        <span className={styles.icon}>✦</span>
        Modifier via IA
      </button>

      <div className={`${styles.expandArea} ${expanded ? styles.open : ""}`}>
        <div className={styles.inner}>
          <textarea
            ref={textareaRef}
            className={`${styles.textarea} ${error ? styles.textareaError : ""}`}
            placeholder="Ex : augmente de 2°C toutes les pièces pendant 2h à partir de 18h"
            value={instruction}
            onChange={(e) => {
              setInstruction(e.target.value);
              if (error) setError(null);
            }}
            onKeyDown={handleKeyDown}
            rows={2}
            disabled={loading}
          />
          {error && (
            <p className={styles.errorMessage}>{error}</p>
          )}
          <div className={styles.inputFooter}>
            <button
              className={styles.submitBtn}
              onClick={handleSubmit}
              disabled={loading || !instruction.trim()}
              type="button"
            >
              {btnLabel}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
