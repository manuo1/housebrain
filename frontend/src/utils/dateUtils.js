export function formatLocalDate(isoString) {
  if (!isoString) return "N/A";
  const date = new Date(isoString);
  return date.toLocaleString(undefined, {
    dateStyle: "short",
    timeStyle: "medium",
  });
}
