export function toast(title, message) {
  const toastElement = document.getElementById("toast");
  const toastTitleElement = document.getElementById("toast-title");
  const toastContentElement = document.getElementById("toast-content");

  toastTitleElement.innerHTML = title;
  toastContentElement.innerHTML = message;

  const toast = new bootstrap.Toast(toastElement);
  toast.show();
}