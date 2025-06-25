import { fetchJson } from "./fetchJson";
import DailyIndexes from "../models/DailyIndexes";

async function fetchDailyIndexes(date, step = 1) {
  // Validation du step avant l'envoi de la requête
  if (!DailyIndexes.ALLOWED_STEPS.includes(step)) {
    throw new Error(
      `Invalid step value: ${step}. Allowed values: ${DailyIndexes.ALLOWED_STEPS.join(
        ", "
      )}`
    );
  }

  const params = new URLSearchParams({ date, step: step.toString() });

  try {
    const data = await fetchJson(`/api/consumption/daily/?${params}`);

    // Validation de la structure de la réponse
    if (!data || typeof data !== "object") {
      throw new Error("Invalid response format from API");
    }

    // Création de l'instance DailyIndexes avec les données de l'API
    return new DailyIndexes(data.date, data.step, data.data, data.totals);
  } catch (error) {
    console.error("Error fetching daily indexes:", error);
    throw error;
  }
}

export default fetchDailyIndexes;
