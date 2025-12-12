export default async function duplicateHeatingPlan(
  duplicationData,
  accessToken
) {
  const response = await fetch('/api/heating/plans/duplicate/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify(duplicationData),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}
