import { useState } from "react";
import { ChangedEquipment } from "../../../services/saveDailyEquipmentPlan";
import styles from "./DuplicationChat.module.scss";

type Role = "user" | "assistant";

interface Echange {
  role: Role;
  content: string;
}

type DuplicationStep = "clarify" | "to_validate" | "validate" | "error";

export interface PropagationSeed {
  equipments: ChangedEquipment[];
  nonce: number;
}

interface DuplicationChatProps {
  sourceDate: string;
  onDuplicationSuccess: () => void;
  propagationSeed?: PropagationSeed | null;
}

function joinEquipmentNamesFr(names: string[]): string {
  if (names.length <= 1) return names[0] ?? "";
  return names.slice(0, -1).join(", ") + " et " + names[names.length - 1];
}

function buildPropagationEchanges(equipments: ChangedEquipment[]): Echange[] {
  const namesFr = joinEquipmentNamesFr(equipments.map((e) => e.name));
  return [
    {
      role: "user",
      content: `Je viens de modifier le planning de ${namesFr}. Je veux propager ce changement sur d'autres jours.`,
    },
    { role: "assistant", content: "Précisez la période." },
  ];
}

// NOTE: this chat is not wired to a backend yet (no generic equivalent of
// /api/ai/heating/duplicate/ exists for planning/api). handleSend/
// handleValidate are intentionally no-ops — visible and interactive, but
// silent, so the UI matches heating's page without calling anything.
export default function DuplicationChat({ sourceDate: _sourceDate, onDuplicationSuccess: _onDuplicationSuccess, propagationSeed }: DuplicationChatProps) {
  const [echanges] = useState<Echange[]>(() =>
    propagationSeed && propagationSeed.equipments.length > 0
      ? buildPropagationEchanges(propagationSeed.equipments)
      : []
  );
  const [step] = useState<DuplicationStep | null>(
    propagationSeed && propagationSeed.equipments.length > 0 ? "clarify" : null
  );
  const [inputValue, setInputValue] = useState("");

  const handleSend = () => {
    // not wired yet
  };

  const handleValidate = () => {
    // not wired yet
  };

  const handleReject = () => {
    // not wired yet
  };

  return (
    <div className={styles.duplicationChat}>
      <h3>Dupliquer via IA</h3>

      <div className={styles.messageList}>
        {echanges.length === 0 && (
          <p className={styles.placeholder}>
            Décrivez la duplication souhaitée (ex : "copie le planning du chauffe-eau tous les mercredis
            jusqu'à fin septembre")
          </p>
        )}
        {echanges.map((e, i) => (
          <div key={i} className={e.role === "user" ? styles.userMsg : styles.assistantMsg}>
            {e.content}
          </div>
        ))}
      </div>

      {step === "to_validate" ? (
        <div className={styles.validationButtons}>
          <button onClick={handleValidate}>Oui</button>
          <button onClick={handleReject}>Non</button>
        </div>
      ) : (
        <div className={styles.inputRow}>
          <input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Votre instruction..."
          />
          <button onClick={handleSend} disabled={!inputValue.trim()}>Envoyer</button>
        </div>
      )}
    </div>
  );
}
