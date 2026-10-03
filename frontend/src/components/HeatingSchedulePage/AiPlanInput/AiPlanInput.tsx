import { useState, useRef, useEffect } from "react";
import styles from "./AiPlanInput.module.scss";

interface AiPlanInputProps {
  onSubmit: (instruction: string) => Promise<void>;
  disabled?: boolean;
  locked?: boolean;
}

export default function AiPlanInput({ onSubmit, disabled, locked = false }: AiPlanInputProps) {
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
    if (loading) return;
    if (expanded) {
      setExpanded(false);
      setInstruction("");
      setError(null);
    } else {
      setExpanded(true);
    }
  };

  const handleSubmit = async () => {
    if (locked || !instruction.trim() || loading) return;
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
      if (loading) return;
      setExpanded(false);
      setInstruction("");
      setError(null);
    }
  };

  const btnLabel = loading ? "Réflexion..." : "Appliquer";

  return (
    <div className={styles.wrapper}>
      <button
        className={`${styles.toggleBtn} ${expanded ? styles.active : ""} ${locked ? styles.locked : ""}`}
        onClick={handleToggle}
        disabled={disabled}
        type="button"
      >
        <span className={styles.icon}>{locked ? "🔒" : "✦"}</span>
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
            disabled={loading || locked}
          />
          {locked && (
            <p className={styles.lockedHint}>Connectez-vous pour utiliser cette fonction</p>
          )}
          {error && (
            <p className={styles.errorMessage}>{error}</p>
          )}
          <div className={styles.inputFooter}>
            <button
              className={styles.submitBtn}
              onClick={handleSubmit}
              disabled={locked || loading || !instruction.trim()}
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
