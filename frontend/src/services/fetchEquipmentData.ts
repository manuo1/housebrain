import { fetchJson } from "./fetchJson";
import Equipment, { EquipmentGroupsRaw } from "../models/Equipment";

async function fetchEquipmentData(): Promise<Equipment[]> {
  try {
    const data = await fetchJson<EquipmentGroupsRaw>("/api/equipment/");

    if (typeof data !== "object" || data === null || Array.isArray(data)) {
      throw new Error("Invalid response format from API: expected an object of groups");
    }

    return Object.entries(data).flatMap(([interactionType, items]) =>
      items.map((item) => new Equipment(item, interactionType))
    );
  } catch (error) {
    console.error("Error fetching equipment data:", error);
    throw error;
  }
}

export default fetchEquipmentData;
