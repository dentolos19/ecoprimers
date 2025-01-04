const toasterElement = document.getElementById("toaster");

export function toast(message, category) {
  // const toastElement = document.getElementById("toast");
  // const toastTitleElement = document.getElementById("toast-title");
  // const toastContentElement = document.getElementById("toast-content");

  // toastTitleElement.innerHTML = title;
  // toastContentElement.innerHTML = message;

  // const toast = new bootstrap.Toast(toastElement);
  // toast.show();

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

  toasterElement.appendChild(toast);

  // Remove hidden existing toasts
  const hiddenToastElements = toasterElement.getElementsByClassName("hide");
  for (const element of hiddenToastElements) {
    element.remove();
  }
}