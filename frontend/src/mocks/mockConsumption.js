export const mockConsumption = {
  period: 'jour',
  type: 'watt',
  startDate: '2024-01-01',

  axisY: {
    labels: ['0 W', '50 W', '100 W', '150 W', '200 W'],
  },

  axisX: {
    labels: ['00:00', '06:00', '12:00', '18:00', '24:00'],
  },

  values: [
    {
      width: 4.16,
      area_height: 60,
      area_color: '#3b82f6',
      line_height: -20,
      line_color: '#3b82f6',
      tooltip: { title: '00:00 -> 01:00', content: ['120 Wh', 'Coût: 0.25€'] },
    },
    {
      width: 4.16,
      area_height: 40,
      area_color: '#22c55e',
      line_height: 40,
      line_color: '#22c55e',
      tooltip: { title: '01:00 -> 02:00', content: ['80 Wh', 'Coût: 0.15€'] },
    },
    {
      width: 4.16,
      area_height: 80,
      area_color: '#3b82f6',
      line_height: 15,
      line_color: '#3b82f6',
      tooltip: { title: '02:00 -> 03:00', content: ['160 Wh', 'Coût: 0.35€'] },
    },
    {
      width: 4.16,
      area_height: 95,
      area_color: '#22c55e',
      line_height: -75,
      line_color: '#22c55e',
      tooltip: { title: '03:00 -> 04:00', content: ['160 Wh', 'Coût: 0.35€'] },
    },
    {
      width: 4.16,
      area_height: 20,
      area_color: '#3b82f6',
      line_height: 60,
      line_color: '#3b82f6',
      tooltip: { title: '04:00 -> 05:00', content: ['80 Wh', 'Coût: 0.15€'] },
    },
    {
      width: 4.16,
      area_height: 80,
      area_color: '#3b82f6',
      line_height: -40,
      line_color: '#3b82f6',
      tooltip: { title: '04:00 -> 05:00', content: ['80 Wh', 'Coût: 0.15€'] },
    },
    {
      width: 4.16,
      area_height: 40,
      area_color: '#3b82f6',
      line_height: -20,
      line_color: '#3b82f6',
      tooltip: { title: '04:00 -> 05:00', content: ['80 Wh', 'Coût: 0.15€'] },
    },
    {
      width: 4.16,
      area_height: 20,
      area_color: '#3b82f6',
      line_height: -20,
      line_color: '#3b82f6',
      tooltip: { title: '04:00 -> 05:00', content: ['80 Wh', 'Coût: 0.15€'] },
    },
    {
      width: 4.16,
      area_height: 0,
      area_color: '#3b82f6',
      line_height: 0,
      line_color: '#3b82f6',
      tooltip: { title: '04:00 -> 05:00', content: ['80 Wh', 'Coût: 0.15€'] },
    },
  ],
};
