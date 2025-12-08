import DailyHeatingPlan from '../models/DailyHeatingPlan';

const rawMockData = {
  date: '2025-12-07',
  rooms: [
    {
      id: 1,
      name: 'Salon',
      mode: 'temp',
      slots: [
        { start: '06:00', end: '08:30', value: 20 },
        { start: '18:00', end: '21:30', value: 21 },
      ],
    },
    {
      id: 2,
      name: 'Chambre',
      mode: 'temp',
      slots: [
        { start: '06:00', end: '08:30', value: 19 },
        { start: '18:00', end: '21:30', value: 22 },
      ],
    },
    {
      id: 3,
      name: 'Cuisine',
      mode: 'temp',
      slots: [{ start: '07:00', end: '10:30', value: 18 }],
    },
    {
      id: 4,
      name: 'Salle de bain',
      mode: 'onoff',
      slots: [
        { start: '06:00', end: '08:00', value: 'on' },
        { start: '14:30', end: '17:00', value: 'on' },
      ],
    },
    {
      id: 5,
      name: 'Bureau',
      mode: 'temp',
      slots: [{ start: '08:30', end: '17:00', value: 20 }],
    },
    {
      id: 6,
      name: 'Chambre 2',
      mode: 'temp',
      slots: [
        { start: '06:00', end: '08:30', value: 19 },
        { start: '18:00', end: '21:30', value: 21 },
      ],
    },
    {
      id: 7,
      name: "Salle d'eau",
      mode: 'onoff',
      slots: [{ start: '06:45', end: '08:15', value: 'on' }],
    },
    {
      id: 8,
      name: 'Entrée',
      mode: 'temp',
      slots: [{ start: '06:00', end: '09:00', value: 17 }],
    },
    {
      id: 9,
      name: 'Couloir',
      mode: 'temp',
      slots: [{ start: '06:00', end: '18:00', value: 17 }],
    },
    {
      id: 10,
      name: 'Buanderie',
      mode: 'onoff',
      slots: [{ start: '09:30', end: '10:45', value: 'on' }],
    },
  ],
};

const mockDailyHeatingPlan = new DailyHeatingPlan(rawMockData);

export default mockDailyHeatingPlan;
