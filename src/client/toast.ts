const toasterElement = document.getElementById("toaster");

export function toast(message: string, category: string) {
  if (!toasterElement) return;

  const toast = document.createElement("div");
  toast.classList.add("m-0", "toast", `border-${category}`, "show");

  const toastContainer = document.createElement("div");
  toastContainer.classList.add("d-flex");

  const toastBody = document.createElement("div");
  toastBody.classList.add("toast-body");
  toastBody.textContent = message;

  const toastButton = document.createElement("button");
  toastButton.classList.add("m-auto", "me-2", "btn-close");
  toastButton.setAttribute("data-bs-dismiss", "toast");
  toastButton.setAttribute("aria-label", "Close");

  toastContainer.append(toastBody, toastButton);
  toast.appendChild(toastContainer);
  toasterElement.appendChild(toast);

  let hidden = toasterElement.querySelector(".hide");
  while (hidden) {
    hidden.remove();
    hidden = toasterElement.querySelector(".hide");
  }
}
