import HeatingCalendar from '../models/HeatingCalendar';

const rawMockData = {
  year: 2025,
  month: 12,
  today: '2025-12-08',
  days: [
    // Décembre
    { date: '2025-12-01', status: 'normal' },
    { date: '2025-12-02', status: 'normal' },
    { date: '2025-12-03', status: 'normal' },
    { date: '2025-12-04', status: 'normal' },
    { date: '2025-12-05', status: 'normal' },
    { date: '2025-12-06', status: 'normal' },
    { date: '2025-12-07', status: 'normal' },
    { date: '2025-12-08', status: 'normal' },
    { date: '2025-12-09', status: 'normal' },
    { date: '2025-12-10', status: 'normal' },
    { date: '2025-12-11', status: 'normal' },
    { date: '2025-12-12', status: 'normal' },
    { date: '2025-12-13', status: 'different' },
    { date: '2025-12-14', status: 'different' },
    { date: '2025-12-15', status: 'normal' },
    { date: '2025-12-16', status: 'normal' },
    { date: '2025-12-17', status: 'normal' },
    { date: '2025-12-18', status: 'normal' },
    { date: '2025-12-19', status: 'normal' },
    { date: '2025-12-20', status: 'different' },
    { date: '2025-12-21', status: 'different' },
    { date: '2025-12-22', status: 'different' },
    { date: '2025-12-23', status: 'different' },
    { date: '2025-12-24', status: 'normal' },
    { date: '2025-12-25', status: 'different' },
    { date: '2025-12-26', status: 'different' },
    { date: '2025-12-27', status: 'normal' },
    { date: '2025-12-28', status: 'normal' },
    { date: '2025-12-29', status: 'normal' },
    { date: '2025-12-30', status: 'normal' },
    { date: '2025-12-31', status: 'normal' },

    // Semaine incomplète janvier 2026
    { date: '2026-01-01', status: 'empty' },
    { date: '2026-01-02', status: 'empty' },
    { date: '2026-01-03', status: 'empty' },
    { date: '2026-01-04', status: 'empty' },
  ],
};

const mockHeatingCalendar = new HeatingCalendar(rawMockData);

export default mockHeatingCalendar;
