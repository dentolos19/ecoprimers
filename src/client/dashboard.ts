import { renderMarkdown } from "./markdown";
import { humanizeMonthYear } from "./utils.js";

type Month = { month: string; count: number };
type Analysis = {
  totalUsers: number;
  totalEvents: number;
  totalPosts: number;
  totalProducts: number;
  monthlyUsers: Month[];
  monthlySignups: Month[];
  monthlyTransactions: Month[];
};

const activeUsers = document.querySelector<HTMLElement>("#activeUsers");
const platformEvents = document.querySelector<HTMLElement>("#platformEvents");
const communityPosts = document.querySelector<HTMLElement>("#communityPosts");
const rewardProducts = document.querySelector<HTMLElement>("#rewardProducts");
const monthlyUsers = document.querySelector<HTMLCanvasElement>("#monthlyUsers");
const monthlySignups = document.querySelector<HTMLCanvasElement>("#monthlySignups");
const monthlyTransactions = document.querySelector<HTMLCanvasElement>("#monthlyTransactions");
const recommendations = document.querySelector<HTMLFormElement>("#recommendations");
const recommendationOutput = document.querySelector<HTMLElement>("#recommendations-output");
if (
  !activeUsers ||
  !platformEvents ||
  !communityPosts ||
  !rewardProducts ||
  !monthlyUsers ||
  !monthlySignups ||
  !monthlyTransactions ||
  !recommendations ||
  !recommendationOutput
)
  throw new Error("Missing dashboard elements.");

async function loadAnalysis() {
  if (
    !activeUsers ||
    !platformEvents ||
    !communityPosts ||
    !rewardProducts ||
    !monthlyUsers ||
    !monthlySignups ||
    !monthlyTransactions
  )
    return;
  try {
    const response = await fetch("/api/analysis");
    if (!response.ok) throw new Error(`Could not load analysis: ${response.status}`);
    const data: Analysis = await response.json();
    activeUsers.textContent = String(data.totalUsers);
    platformEvents.textContent = String(data.totalEvents);
    communityPosts.textContent = String(data.totalPosts);
    rewardProducts.textContent = String(data.totalProducts);

    for (const [element, rows, label] of [
      [monthlyUsers, data.monthlyUsers, "Users per month"],
      [monthlySignups, data.monthlySignups, "Signups per month"],
      [monthlyTransactions, data.monthlyTransactions, "Transactions per month"],
    ] satisfies [HTMLCanvasElement, Month[], string][]) {
      new Chart(element, {
        type: "line",
        data: {
          labels: rows.map((row) => humanizeMonthYear(row.month)),
          datasets: [{ label, data: rows.map((row) => row.count) }],
        },
        options: { scales: { y: { beginAtZero: true } } },
      });
    }
  } catch (error) {
    console.error(error);
    for (const element of [activeUsers, platformEvents, communityPosts, rewardProducts])
      element.textContent = "Unavailable";
  }
}

recommendations.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!recommendationOutput) return;
  recommendationOutput.textContent = "Loading...";
  try {
    const response = await fetch("/api/analysis/recommendations");
    if (!response.ok) throw new Error(`Could not load recommendations: ${response.status}`);
    const data: unknown = await response.json();
    if (typeof data !== "object" || data === null || !("response" in data) || typeof data.response !== "string")
      throw new Error("Invalid recommendations response.");
    recommendationOutput.innerHTML = renderMarkdown(data.response);
  } catch (error) {
    console.error(error);
    recommendationOutput.textContent = "Unable to load recommendations.";
  }
});

void loadAnalysis();
