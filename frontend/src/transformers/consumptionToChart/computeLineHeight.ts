function computeLineHeight(currentHeight: number, nextHeight: number | null | undefined): number {
  if (nextHeight === null || nextHeight === undefined) return 0;
  return nextHeight - currentHeight;
}

export default computeLineHeight;
