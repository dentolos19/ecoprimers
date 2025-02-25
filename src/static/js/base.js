const toasterElement = document.getElementById("toaster");

export function toast(message, category) {
  // Create toast element
  const toast = document.createElement("div");
  toast.classList.add("m-0");
  toast.classList.add("toast");
  toast.classList.add(`border-${category}`);
  toast.classList.add("show");

  const toastContainer = document.createElement("div");
  toastContainer.classList.add("d-flex");

  const toastBody = document.createElement("div");
  toastBody.classList.add("toast-body");
  toastBody.innerHTML = message;

  const toastButton = document.createElement("button");
  toastButton.classList.add("m-auto");
  toastButton.classList.add("me-2");
  toastButton.classList.add("btn-close");
  toastButton.setAttribute("data-bs-dismiss", "toast");

  toastContainer.appendChild(toastBody);
  toastContainer.appendChild(toastButton);
  toast.appendChild(toastContainer);

  // Add toast to the toaster
  toasterElement.appendChild(toast);

  // Remove hidden toast elments
  const hiddenToastElements = toasterElement.getElementsByClassName("hide");
  for (const element of hiddenToastElements) {
    toasterElement.removeChild(element);
  }
}

document.addEventListener("DOMContentLoaded", function () {
  // Enable Bootstrap Tooltips
  const tooltipTriggers = document.querySelectorAll("[data-bs-toggle='tooltip']");
  const tooltipList = [...tooltipTriggers].map((tooltipTrigger) => new bootstrap.Tooltip(tooltipTrigger));

  // Add placeholder images
  document.querySelectorAll("img").forEach((img) => {
    img.onerror = function () {
      this.src = "/static/img/placeholder.png";
      this.onerror = null; // Prevent infinite loop
    };
  });

  document.querySelectorAll("form button[type='submit'][data-confirm]").forEach((element) => {
    element.addEventListener("click", (event) => {
      const message = element.getAttribute("data-confirm");
      if (!confirm(message)) {
        event.preventDefault();
      }
    });
  });
});