import { renderMarkdown } from "./markdown";
import { toast } from "./toast";

type Message = { id: string; sender_id: string; receiver_id: string; message: string; is_visible: boolean };

let reconnectDelay = 1000;
let reconnectTimer: number | undefined;
let pingTimer: number | undefined;
let pollTimer: number | undefined;
let currentRecipientId: string | null = null;
let currentSenderId: string | null = null;

function isMessage(value: unknown): value is Message {
  return (
    typeof value === "object" &&
    value !== null &&
    "id" in value &&
    typeof value.id === "string" &&
    "sender_id" in value &&
    typeof value.sender_id === "string" &&
    "receiver_id" in value &&
    typeof value.receiver_id === "string" &&
    "message" in value &&
    typeof value.message === "string" &&
    "is_visible" in value &&
    typeof value.is_visible === "boolean"
  );
}

function displayMessage(message: Message) {
  const messageSpace = document.querySelector<HTMLElement>(".message-space");
  if (!messageSpace || !message.is_visible) return;
  const sent = message.sender_id === currentSenderId && message.receiver_id === currentRecipientId;
  const received = message.sender_id === currentRecipientId && message.receiver_id === currentSenderId;
  if (!sent && !received) return;

  const block = document.createElement("div");
  block.className = `message-block ${sent ? "you" : "other-person"}`;
  block.id = message.id;
  const form = document.createElement("form");
  form.method = "POST";
  form.action = `/community/messages/${encodeURIComponent(message.receiver_id)}/${encodeURIComponent(message.id)}`;
  const card = document.createElement("div");
  card.className = "message card rounded-3";
  const body = document.createElement("div");
  body.className = "card-body";
  const content = document.createElement("div");
  content.className = "card-text";
  content.innerHTML = renderMarkdown(message.message);
  body.appendChild(content);
  if (sent) {
    const button = document.createElement("button");
    button.type = "submit";
    button.className = "btn btn-danger btn-sm float-end";
    button.textContent = "Delete";
    body.appendChild(button);
  }
  card.appendChild(body);
  form.appendChild(card);
  block.appendChild(form);
  messageSpace.appendChild(block);
  messageSpace.scrollTop = messageSpace.scrollHeight;
}

function connectSocket() {
  if (!currentRecipientId) return;
  window.clearTimeout(reconnectTimer);
  const protocol = location.protocol === "https:" ? "wss" : "ws";
  const socket = new WebSocket(`${protocol}://${location.host}/ws/dm/${encodeURIComponent(currentRecipientId)}`);
  socket.addEventListener("open", () => {
    reconnectDelay = 1000;
    window.clearInterval(pollTimer);
    pollTimer = undefined;
    window.clearInterval(pingTimer);
    pingTimer = window.setInterval(() => {
      if (socket.readyState === WebSocket.OPEN) socket.send(JSON.stringify({ type: "ping" }));
    }, 30000);
  });
  socket.addEventListener("message", (event) => {
    if (typeof event.data !== "string") return;
    let payload: unknown;
    try {
      payload = JSON.parse(event.data);
    } catch {
      return;
    }
    if (typeof payload !== "object" || payload === null || !("type" in payload)) return;
    if (payload.type === "message" && "data" in payload && isMessage(payload.data)) {
      if (!document.getElementById(payload.data.id)) displayMessage(payload.data);
    } else if (payload.type === "message_deleted" || payload.type === "message_restored") {
      location.reload();
    }
  });
  socket.addEventListener("close", () => {
    window.clearInterval(pingTimer);
    startPolling();
    reconnectTimer = window.setTimeout(connectSocket, reconnectDelay);
    reconnectDelay = Math.min(reconnectDelay * 2, 30000);
  });
  socket.addEventListener("error", () => socket.close());
}

function startPolling() {
  if (pollTimer !== undefined) return;
  void loadMessages();
  pollTimer = window.setInterval(loadMessages, 3000);
}

async function loadMessages() {
  if (!currentSenderId || !currentRecipientId) return;
  try {
    const params = new URLSearchParams({ sender_id: currentSenderId, receiver_id: currentRecipientId });
    const response = await fetch(`/api/messages?${params}`);
    if (!response.ok) throw new Error(`Could not load messages: ${response.status}`);
    const messages: unknown = await response.json();
    if (!Array.isArray(messages)) throw new Error("Invalid message response.");
    for (const message of messages.reverse()) {
      if (!isMessage(message)) continue;
      const existing = document.getElementById(message.id);
      if (!message.is_visible) existing?.remove();
      else if (!existing) displayMessage(message);
    }
  } catch (error) {
    console.error(error);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const sender = document.querySelector<HTMLInputElement>("#sender-id");
  const receiver = document.querySelector<HTMLInputElement>("#receiver-id");
  const input = document.querySelector<HTMLInputElement>("input#message");
  if (!sender || !receiver || !input) return;
  currentSenderId = sender.value;
  currentRecipientId = receiver.value;
  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      sendMessage();
    }
  });
  if (["localhost", "127.0.0.1"].includes(location.hostname)) startPolling();
  else {
    void loadMessages();
    connectSocket();
  }
});

async function sendMessage() {
  const input = document.querySelector<HTMLInputElement>("input#message");
  if (!input || !currentRecipientId) return;
  const content = input.value;
  if (!content.trim()) return;
  input.value = "";
  try {
    const response = await fetch("/api/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "same-origin",
      body: JSON.stringify({ receiver_id: currentRecipientId, content }),
    });
    if (!response.ok) throw new Error(`Could not send message: ${response.status}`);
    const message: unknown = await response.json();
    if (!isMessage(message)) throw new Error("Invalid message response.");
    if (!document.getElementById(message.id)) displayMessage(message);
  } catch (error) {
    if (!input.value) input.value = content;
    console.error(error);
    toast("Unable to send the message. Please try again.", "danger");
  }
}

window.sendMessage = sendMessage;
