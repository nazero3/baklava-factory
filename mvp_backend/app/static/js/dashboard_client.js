const KPI_FIELDS = [
  "raw_stock_kg",
  "finished_stock_kg",
  "produced_kg",
  "waste_kg",
  "sales_kg",
];

export async function fetchDashboardSummary(accessToken) {
  const res = await fetch("/dashboard/daily-summary", {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!res.ok) {
    throw new Error(res.statusText || `HTTP ${res.status}`);
  }

  const data = await res.json();
  return KPI_FIELDS.reduce((normalized, field) => {
    normalized[field] = Number(data[field]);
    return normalized;
  }, {});
}
