export { toast } from "./toast";

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-bs-toggle='tooltip']").forEach((element) => new bootstrap.Tooltip(element));

  document.querySelectorAll("img").forEach((img) => {
    img.onerror = () => {
      img.src = "/static/img/placeholder.png";
      img.onerror = null;
    };
  });

  document.querySelectorAll("form button[type='submit'][data-confirm]").forEach((element) => {
    element.addEventListener("click", (event) => {
      const message = element.getAttribute("data-confirm");
      if (message !== null && !confirm(message)) event.preventDefault();
    });
  });
});
