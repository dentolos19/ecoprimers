import { marked } from "https://cdn.jsdelivr.net/npm/marked/lib/marked.esm.js";

import { toast } from "./base.js";

// messages.js
let socket = null;
let reconnectDelay = 1000;
let reconnectTimer = null;
let pingTimer = null;

// Store current chat state
let currentRecipientId = null;
let currentSenderId = null;

function displayMessage(message) {
  const messageSpace = document.querySelector(".message-space");
  const messageBlock = document.createElement("div");
  messageBlock.className = `message-block ${message.sender_id === currentSenderId ? "you" : "other-person"}`;
  messageBlock.id = message.id;

  if (message.sender_id == currentSenderId && message.is_visible) {
    messageBlock.innerHTML = `
    <form action="/community/messages/${message.receiver_id}/${message.id}" method="POST">
      <div class="message card rounded-3">
        <div class="card-body">
          <p class="card-text">${marked.parse(message.message)}</p>
          <button type="submit" class="btn btn-danger btn-sm float-end">Delete</button>
        </div>
      </div>
    </form>
    `;
    console.log(
      `test: logged in user = sender, sender id = ${message.sender_id}, current sender id = ${currentSenderId}`,
    );
  } else if (message.receiver_id == currentSenderId && message.is_visible) {
    messageBlock.innerHTML = `
    <form action="/community/messages/${message.receiver_id}/${message.id}" method="POST">
      <div class="message card rounded-3">
        <div class="card-body">
          <p class="card-text">${marked.parse(message.message)}</p>
        </div>
      </div>
    </form>
    `;
    console.log(
      `test: logged in user = receiver, sender id = ${message.sender_id}, current sender id = ${currentSenderId}`,
    );
  }
  messageSpace.appendChild(messageBlock);
  messageSpace.scrollTop = messageSpace.scrollHeight;
}

function connectSocket() {
  clearTimeout(reconnectTimer);

  const protocol = location.protocol === "https:" ? "wss" : "ws";
  socket = new WebSocket(`${protocol}://${location.host}/ws/dm/${currentRecipientId}`);

  socket.addEventListener("open", () => {
    console.log("Connected to WebSocket server");
    reconnectDelay = 1000;

    clearInterval(pingTimer);
    pingTimer = setInterval(() => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: "ping" }));
      }
    }, 30000);
  });

  socket.addEventListener("message", (event) => {
    let payload;
    try {
      payload = JSON.parse(event.data);
    } catch (error) {
      console.error(error);
      return;
    }

    if (payload.type === "message") {
      const message = payload.data;

      // Check if this message belongs to current chat
      if (
        message.sender_id === currentRecipientId ||
        (message.sender_id === currentSenderId && message.receiver_id === currentRecipientId)
      ) {
        // The sender already rendered the POST response, so skip duplicates.
        if (!document.getElementById(message.id)) {
          displayMessage(message);
        }
      }
    } else if (payload.type === "message_deleted" || payload.type === "message_restored") {
      location.reload();
    }
  });

  socket.addEventListener("close", () => {
    console.log("Disconnected from WebSocket server");
    clearInterval(pingTimer);

    reconnectTimer = setTimeout(() => {
      console.log(`Reconnecting in ${reconnectDelay}ms`);
      connectSocket();
    }, reconnectDelay);
    reconnectDelay = Math.min(reconnectDelay * 2, 30000);
  });

  socket.addEventListener("error", (error) => {
    console.error(error);
    socket.close();
  });
}

function loadMessages() {
  fetch(`/api/messages?sender_id=${currentSenderId}&receiver_id=${currentRecipientId}`)
    .then((response) => response.json())
    .then((messages) => {
      messages.forEach((message) => {
        if (!document.getElementById(message.id)) {
          displayMessage(message);
        }
      });
    });
}

document.addEventListener("DOMContentLoaded", () => {
  const senderElement = document.querySelector("#sender-id");
  const receiverElement = document.querySelector("#receiver-id");

  if (!senderElement || !receiverElement) {
    return;
  }

  currentSenderId = senderElement.value;
  currentRecipientId = receiverElement.value;
  console.log(currentRecipientId);

  loadMessages();

  const inputElement = document.querySelector("input#message");

  inputElement.addEventListener("keypress", (event) => {
    if (event.key === "Enter") {
      event.preventDefault(); // Prevent the default form submission
      sendMessage(); // Trigger the sendMessage function
    }
  });

  if (["localhost", "127.0.0.1"].includes(location.hostname)) {
    setInterval(loadMessages, 3000);
  } else {
    connectSocket();
  }
});

function sendMessage() {
  console.log("running sendMessage()");
  const inputElement = document.querySelector("input#message");
  const content = inputElement.value;
  inputElement.value = "";
  console.log(content);

  // The server rejects empty or whitespace-only content.
  if (!content.trim()) {
    return;
  }

  fetch("/api/messages", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "same-origin",
    body: JSON.stringify({
      receiver_id: currentRecipientId,
      content: content,
    }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(response.statusText);
      }

      return response.json();
    })
    .then((message) => {
      // The WebSocket echo may have rendered the message already.
      if (!document.getElementById(message.id)) {
        displayMessage(message);
      }
    })
    .catch((error) => {
      console.error(error);
      toast("An error had occurred! Please check the console for more information.", "danger");
    });
}

// The template's send button calls sendMessage() inline.
window.sendMessage = sendMessage;
