import { marked } from "https://cdn.jsdelivr.net/npm/marked/lib/marked.esm.js";
import { toast } from "./base.js";

const messagesElement = document.getElementById("messages");
const formElement = document.getElementById("form");

const messages = [
  {
    role: "bot",
    content: "Hello! How can I help you today?",
  },
];

function createMessageElement(name, content) {
  const card = document.createElement("div");
  card.classList.add("card");
  card.classList.add("container");

  const cardBody = document.createElement("div");
  cardBody.classList.add("card-body");

  const cardTitle = document.createElement("h5");
  cardTitle.classList.add("card-title");
  cardTitle.innerHTML = name;

  const cardText = document.createElement("p");
  cardText.classList.add("card-text");
  cardText.innerHTML = content;

  cardBody.appendChild(cardTitle);
  cardBody.appendChild(cardText);
  card.appendChild(cardBody);

  return card;
}

function renderMessages() {
  // Clear chat
  messagesElement.innerHTML = "";

  // Render messages
  messages.forEach(({ role, content }) => {
    const name = role === "bot" ? "Customer Service" : "You";
    const messageElement = createMessageElement(name, marked.parse(content));
    messagesElement.appendChild(messageElement);
  });

  // Scroll to bottom of chat
  messagesElement.scrollTop = messagesElement.scrollHeight;
}

function sendMessage(event) {
  // Prevent default behavior; refresh page
  event.preventDefault();

  // Get form data
  const data = new FormData(event.target);
  const entries = Object.fromEntries(data.entries());
  const { content } = entries;

  if (!content) {
    toast("Error", "Please enter a message!");
    return;
  }

  // Clear fields
  event.target.reset();

  // Add user message to chat
  messages.push({ role: "user", content });
  renderMessages();

  // Send data to server
  fetch("/api/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      prompt: content,
      history: messages.map((message) => {
        return { role: message.role, content: message.content };
      }),
    }),
  })
    .then((res) => {
      // Handle errors
      if (!res.ok) return Error(res.statusText);

      // Parse response
      return res.json();
    })
    .then((data) => {
      // Parse data
      const { response } = data;

      // Add bot response to chat
      messages.push({ role: "bot", content: response });
    })
    .catch((error) => {
      toast("Error", error);
    })
    .finally(() => {
      renderMessages();
    });
}

formElement.addEventListener("submit", sendMessage);

renderMessages();