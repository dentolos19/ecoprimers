export function humanizeMonthYear(value: string) {
  const [year, month] = value.split("-").map(Number);
  const date = new Date(year, month - 1);
  return date.toLocaleString("default", { month: "long", year: "numeric" });
}
