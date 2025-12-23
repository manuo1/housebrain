export const mockConsumption = {
  periode: 'jour',
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
      width: 8.33,
      height: 30,
      fillColor: '#3b82f6',
      borderColor: '#22c55e',
      borderPosition: 'top',
      tooltip: {
        title: '00H00 -> 02H00',
        contenu: [
          '60 Wh consommés',
          'Puissance moyenne : 60 W',
          'Coût : 0,12 €',
        ],
      },
    },
    {
      width: 8.33,
      height: 45,
      fillColor: '#3b82f6',
      borderColor: '#22c55e',
      borderPosition: 'top',
      tooltip: {
        title: '02H00 -> 04H00',
        contenu: [
          '90 Wh consommés',
          'Puissance moyenne : 90 W',
          'Coût : 0,18 €',
        ],
      },
    },
    // ... autres rectangles
  ],
};
