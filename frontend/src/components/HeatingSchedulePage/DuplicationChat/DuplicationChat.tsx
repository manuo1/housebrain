import { useState, useEffect } from "react";
import { useAuth } from "../../../contexts/useAuth";
import duplicateHeatingPlanAi, {
  Echange,
  DuplicationData,
  DuplicationStep,
} from "../../../services/duplicateHeatingPlanAi";
import { ChangedRoom } from "../../../services/saveDailyHeatingPlan";
import styles from "./DuplicationChat.module.scss";

export interface PropagationSeed {
  rooms: ChangedRoom[];
  nonce: number;
}

interface DuplicationChatProps {
  sourceDate: string;
  onDuplicationSuccess: () => void;
  propagationSeed?: PropagationSeed | null;
}

function joinRoomNamesFr(names: string[]): string {
  if (names.length <= 1) return names[0] ?? "";
  return names.slice(0, -1).join(", ") + " et " + names[names.length - 1];
}

function buildPropagationEchanges(rooms: ChangedRoom[]): Echange[] {
  const roomsFr = joinRoomNamesFr(rooms.map((r) => r.name));
  return [
    {
      role: "user",
      content: `Je viens de modifier le planning de ${roomsFr}. Je veux propager ce changement sur d'autres jours.`,
    },
    { role: "assistant", content: "Précisez la période." },
  ];
}

export default function DuplicationChat({ sourceDate, onDuplicationSuccess, propagationSeed }: DuplicationChatProps) {
  const { accessToken, refresh } = useAuth();
  const [echanges, setEchanges] = useState<Echange[]>([]);
  const [step, setStep] = useState<DuplicationStep | null>(null);
  const [data, setData] = useState<DuplicationData | null>(null);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [networkError, setNetworkError] = useState<string | null>(null);

  const resetChat = () => {
    setEchanges([]);
    setStep(null);
    setData(null);
    setInputValue("");
    setNetworkError(null);
  };

  // A new save with changed rooms always overrides whatever conversation was
  // in progress (finished or not) — the propagation offer takes priority.
  useEffect(() => {
    if (!propagationSeed || propagationSeed.rooms.length === 0) return;
    setEchanges(buildPropagationEchanges(propagationSeed.rooms));
    setStep("clarify");
    setData(null);
    setInputValue("");
    setNetworkError(null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [propagationSeed?.nonce]);

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading || !accessToken) return;
    const nextEchanges: Echange[] = [...echanges, { role: "user", content: inputValue.trim() }];
    setEchanges(nextEchanges);
    setInputValue("");
    setIsLoading(true);
    setNetworkError(null);
    try {
      const res = await duplicateHeatingPlanAi(sourceDate, nextEchanges, accessToken, refresh);
      setEchanges(res.echanges);
      setStep(res.step);
      setData(res.data);
    } catch (err) {
      setNetworkError((err as Error).message || "Erreur de connexion, réessayez.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleValidate = async () => {
    if (isLoading || !accessToken) return;
    setIsLoading(true);
    setNetworkError(null);
    try {
      const res = await duplicateHeatingPlanAi(sourceDate, echanges, accessToken, refresh, "validate", data);
      if (res.step === "error") {
        setEchanges(res.echanges);
        setStep(res.step);
      } else {
        onDuplicationSuccess();
        resetChat();
      }
    } catch (err) {
      setNetworkError((err as Error).message || "Erreur de connexion, réessayez.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleReject = () => {
    setStep("clarify");
  };

  return (
    <div className={styles.duplicationChat}>
      <h3>Dupliquer via IA</h3>

      <div className={styles.messageList}>
        {echanges.length === 0 && (
          <p className={styles.placeholder}>
            Décrivez la duplication souhaitée (ex : "copie le planning de la chambre tous les mercredis
            jusqu'à fin septembre")
          </p>
        )}
        {echanges.map((e, i) => (
          <div key={i} className={e.role === "user" ? styles.userMsg : styles.assistantMsg}>
            {e.content}
          </div>
        ))}
      </div>

      {networkError && <p className={styles.errorMessage}>{networkError}</p>}

      {step === "to_validate" ? (
        <div className={styles.validationButtons}>
          <button onClick={handleValidate} disabled={isLoading}>Oui</button>
          <button onClick={handleReject} disabled={isLoading}>Non</button>
        </div>
      ) : step === "error" ? (
        <button className={styles.resetButton} onClick={resetChat}>Recommencer</button>
      ) : (
        <div className={styles.inputRow}>
          <input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            disabled={isLoading}
            placeholder="Votre instruction..."
          />
          <button onClick={handleSend} disabled={isLoading || !inputValue.trim()}>Envoyer</button>
        </div>
      )}
    </div>
  );
}
