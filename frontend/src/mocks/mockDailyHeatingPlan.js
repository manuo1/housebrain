import DailyHeatingPlan from '../models/DailyHeatingPlan';

const rawMockData = {
  date: '2025-12-07',
  rooms: [
    {
      room_id: 1,
      name: 'Salon',
      slots: [
        { start: '06:00', end: '08:30', value: 20 },
        { start: '18:00', end: '21:30', value: 21 },
      ],
    },
    {
      room_id: 2,
      name: 'Chambre',
      slots: [
        { start: '06:00', end: '08:30', value: 19 },
        { start: '18:00', end: '21:30', value: 22 },
      ],
    },
    {
      room_id: 3,
      name: 'Cuisine',
      slots: [{ start: '07:00', end: '10:30', value: 18 }],
    },
    {
      room_id: 4,
      name: 'Salle de bain',
      slots: [
        { start: '06:00', end: '08:00', value: 'on' },
        { start: '14:30', end: '17:00', value: 'on' },
      ],
    },
    {
      room_id: 5,
      name: 'Bureau',
      slots: [{ start: '08:30', end: '17:00', value: 20 }],
    },
    {
      room_id: 6,
      name: 'Chambre 2',
      slots: [
        { start: '06:00', end: '08:30', value: 19 },
        { start: '18:00', end: '21:30', value: 21 },
      ],
    },
    {
      room_id: 7,
      name: "Salle d'eau",
      slots: [{ start: '06:45', end: '08:15', value: 'on' }],
    },
    {
      room_id: 8,
      name: 'Entrée',
      slots: [{ start: '06:00', end: '09:00', value: 17 }],
    },
    {
      room_id: 9,
      name: 'Couloir',
      slots: [{ start: '06:00', end: '18:00', value: 17 }],
    },
    {
      room_id: 10,
      name: 'Buanderie',
      slots: [{ start: '09:30', end: '10:45', value: 'on' }],
    },
  ],
};

const mockDailyHeatingPlan = new DailyHeatingPlan(rawMockData);

export default mockDailyHeatingPlan;
