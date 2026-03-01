import { fetchJson } from "./fetchJson";
import Room, { RoomRaw } from "../models/Room";

async function fetchRoomsData(): Promise<Room[]> {
  try {
    const data = await fetchJson<RoomRaw[]>("/api/rooms/");

    if (!Array.isArray(data)) {
      throw new Error("Invalid response format from API: expected an array");
    }

    return data.map((roomData) => new Room(roomData));
  } catch (error) {
    console.error("Error fetching rooms data:", error);
    throw error;
  }
}

export default fetchRoomsData;
