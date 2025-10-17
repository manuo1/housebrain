import { fetchJson } from './fetchJson';
import Room from '../models/Room';

async function fetchRoomsData() {
  try {
    const data = await fetchJson('/api/rooms/');

    if (!Array.isArray(data)) {
      throw new Error('Invalid response format from API: expected an array');
    }

    return data.map((roomData) => new Room(roomData));
  } catch (error) {
    console.error('Error fetching rooms data:', error);
    throw error;
  }
}

export default fetchRoomsData;
