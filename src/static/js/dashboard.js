import { marked } from "https://cdn.jsdelivr.net/npm/marked/lib/marked.esm.js";

const activeUsersElement = document.querySelector("#activeUsers");
const platformEventsElement = document.querySelector("#platformEvents");
const communityPostsElement = document.querySelector("#communityPosts");
const rewardProductsElement = document.querySelector("#rewardProducts");

const monthlyUsersElement = document.querySelector("#monthlyUsers");
const monthlySignupsElement = document.querySelector("#monthlySignups");
const monthlyTransactionsElement = document.querySelector("#monthlyTransactions");

const recommendationsElement = document.querySelector("#recommendations");

async function loadAnalysis() {
  const response = await fetch("/api/analysis");
  const data = await response.json();

  activeUsersElement.textContent = data.totalUsers;
  platformEventsElement.textContent = data.totalEvents;
  communityPostsElement.textContent = data.totalPosts;
  rewardProductsElement.textContent = data.totalProducts;

  const monthlyUsers = data.monthlyUsers;
  const monthlySignups = data.monthlySignups;
  const monthlyTransactions = data.monthlyTransactions;

  new Chart(monthlyUsersElement, {
    type: "line",
    data: {
      labels: monthlyUsers.map((row) => row.month),
      datasets: [
        {
          label: "Users per month",
          data: monthlyUsers.map((row) => row.count),
        },
      ],
    },
    options: {
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  });

  new Chart(monthlySignupsElement, {
    type: "line",
    data: {
      labels: monthlySignups.map((row) => row.month),
      datasets: [
        {
          label: "Signups per month",
          data: monthlySignups.map((row) => row.count),
        },
      ],
    },
    options: {
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  });

  new Chart(monthlyTransactionsElement, {
    type: "line",
    data: {
      labels: monthlyTransactions.map((row) => row.month),
      datasets: [
        {
          label: "Transactions per month",
          data: monthlyTransactions.map((row) => row.count),
        },
      ],
    },
    options: {
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  });
}

async function generateRecommendations(event) {
  event.preventDefault();

  recommendationsElement.innerHTML = "Loading...";

  const response = await fetch("/api/analysis/recommendations");
  const data = await response.json();

  recommendationsElement.innerHTML = "";
  recommendationsElement.innerHTML = marked.parse(data.response);
}

recommendationsElement.addEventListener("submit", generateRecommendations)

loadAnalysis();