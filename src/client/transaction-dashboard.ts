type TransactionData = {
  transaction_types: string[];
  amounts: number[];
  type_amounts: Record<string, number>;
  dates: string[];
  daily_amounts: number[];
};

const chartData = document.getElementById("transaction-chart-data");
const typesChart = document.querySelector<HTMLCanvasElement>("#transaction-types-chart");
const distributionChart = document.querySelector<HTMLCanvasElement>("#transaction-distribution-chart");
const dailyChart = document.querySelector<HTMLCanvasElement>("#daily-points-chart");
if (!chartData || !typesChart || !distributionChart || !dailyChart)
  throw new Error("Missing transaction chart elements.");
const data: TransactionData = JSON.parse(chartData.textContent || "{}");
const colors: Record<string, string> = { earned: "#28a745", redemption: "#dc3545" };
const colorFor = (type: string) => colors[type] ?? "#6c757d";

new Chart(typesChart, {
  type: "bar",
  data: {
    labels: data.transaction_types,
    datasets: [{ data: data.amounts, backgroundColor: data.transaction_types.map(colorFor) }],
  },
  options: {
    plugins: { legend: { display: false }, title: { display: true, text: "Transaction Analysis by Type" } },
    scales: {
      x: { title: { display: true, text: "Transaction Type" } },
      y: { title: { display: true, text: "Points" } },
    },
  },
});

const types = Object.keys(data.type_amounts);
new Chart(distributionChart, {
  type: "pie",
  data: { labels: types, datasets: [{ data: Object.values(data.type_amounts), backgroundColor: types.map(colorFor) }] },
  options: { plugins: { title: { display: true, text: "Transaction Distribution" } } },
});

new Chart(dailyChart, {
  type: "line",
  data: {
    labels: data.dates,
    datasets: [{ data: data.daily_amounts, borderColor: "#0d6efd", backgroundColor: "#0d6efd" }],
  },
  options: {
    plugins: { legend: { display: false }, title: { display: true, text: "Daily Points Activity" } },
    scales: {
      x: { title: { display: true, text: "Transaction Date" } },
      y: { title: { display: true, text: "Points" } },
    },
  },
});
