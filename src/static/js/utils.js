export function humanizeMonthYear(value) {
  const [year, month] = value.split("-");
  const date = new Date(year, month - 1);
  return date.toLocaleString("default", { month: "long", year: "numeric" });
}