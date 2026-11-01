import type { Tooltip } from "bootstrap";
import type { Chart as ChartClass } from "chart.js";

declare global {
  const bootstrap: { Tooltip: typeof Tooltip };
  const Chart: typeof ChartClass;

  interface Window {
    sendMessage: () => void;
  }
}
