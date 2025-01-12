// messages.js
const socket = io();

// Store current chat state
let currentRecipientId = null;
let currentSenderId = null;

function displayMessage(messageData) {
  const messageSpace = document.querySelector(".message-space");
  const messageBlock = document.createElement("div");
  messageBlock.className = `message-block ${messageData.sender_id === currentSenderId ? "you" : "other-person"}`;

  messageBlock.innerHTML = `
    <div class="message">
      <p>${messageData.message}</p>
      <span class="timestamp">${new Date(messageData.sent_time).toLocaleTimeString()}</span>
    </div>
  `;

  messageSpace.appendChild(messageBlock);
  messageSpace.scrollTop = messageSpace.scrollHeight;
}

document.addEventListener("DOMContentLoaded", function () {
  currentSenderId = document.querySelector("#receiver-id").value;
  currentRecipientId = document.querySelector("#sender-id").value;

  fetch(`/api/messages?sender_id=${currentSenderId}&receiver_id=${currentRecipientId}`)
    .then((response) => {
      return response.json();
    })
    .then((messages) => {
      messages.forEach((message) => displayMessage(message));
    });

  // Socket event listeners
  socket.on("connect", () => {
    console.log("Connected to Socket.IO server");
  });

  socket.on("receive_message", (data) => {
    // TODO: Fix socket updates
    const messageSpace = document.querySelector(".message-space");
    messageSpace.innerHTML = "";
    fetch(`/api/messages?sender_id=${currentSenderId}&receiver_id=${currentRecipientId}`)
      .then((response) => {
        return response.json();
      })
      .then((messages) => {
        messages.forEach((message) => displayMessage(message));
      });
  });
});