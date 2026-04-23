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
    } else {
      setExpanded(true);
    }
  };

  const handleSubmit = async () => {
    if (!instruction.trim() || loading) return;
    setLoading(true);
    try {
      await onSubmit(instruction.trim());
      setInstruction("");
      setExpanded(false);
    } catch (error) {
      console.error("Erreur modification IA:", error);
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
    }
  };

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
            className={styles.textarea}
            placeholder="Ex : augmente de 2°C toutes les pièces pendant 2h à partir de 18h"
            value={instruction}
            onChange={(e) => setInstruction(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={2}
            disabled={loading}
          />
          <div className={styles.inputFooter}>
            <button
              className={styles.submitBtn}
              onClick={handleSubmit}
              disabled={loading || !instruction.trim()}
              type="button"
            >
              {loading ? "Envoi..." : "Appliquer"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
