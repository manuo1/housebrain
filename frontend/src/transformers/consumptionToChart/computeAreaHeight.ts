function computeAreaHeight(value: number | null | undefined, maxValue: number): number {
  if (value === null || value === undefined || maxValue <= 0) {
    return 0;
  }
  return (value / maxValue) * 100;
}

export default computeAreaHeight;
