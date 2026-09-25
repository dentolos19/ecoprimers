const data = JSON.parse(document.getElementById("transaction-chart-data").textContent);
const colors = { earned: "#28a745", redemption: "#dc3545" };
const colorFor = (type) => colors[type] ?? "#6c757d";

new Chart(document.getElementById("transaction-types-chart"), {
  type: "bar",
  data: {
    labels: data.transaction_types,
    datasets: [
      {
        data: data.amounts,
        backgroundColor: data.transaction_types.map(colorFor),
      },
    ],
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
new Chart(document.getElementById("transaction-distribution-chart"), {
  type: "pie",
  data: {
    labels: types,
    datasets: [{ data: Object.values(data.type_amounts), backgroundColor: types.map(colorFor) }],
  },
  options: { plugins: { title: { display: true, text: "Transaction Distribution" } } },
});

new Chart(document.getElementById("daily-points-chart"), {
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
