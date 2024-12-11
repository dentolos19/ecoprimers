import { marked } from "https://cdn.jsdelivr.net/npm/marked/lib/marked.esm.js";

const messagesElement = document.getElementById("messages");
const formElement = document.getElementById("form");

function createMessageElement(name, text) {
  const card = document.createElement("div");
  card.classList.add("card");

  const cardBody = document.createElement("div");
  cardBody.classList.add("card-body");

  const cardTitle = document.createElement("h5");
  cardTitle.classList.add("card-title");
  cardTitle.innerHTML = name;

  const cardText = document.createElement("p");
  cardText.classList.add("card-text");
  cardText.innerHTML = text;

  cardBody.appendChild(cardTitle);
  cardBody.appendChild(cardText);
  card.appendChild(cardBody);

  return card;
}

function handleSubmit(event) {
  // Prevent default behavior; refresh page
  event.preventDefault();

  // Get form data
  const data = new FormData(event.target);
  const entries = Object.fromEntries(data.entries());
  const { content } = entries;

  // Clear fields
  event.target.reset();

  // Add user message to chat
  messagesElement.appendChild(createMessageElement("You", content));

  // Send data to server
  fetch("/api/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ prompt: content, history: [] }),
  })
    .then((res) => {
      // Parse data and handle errors
      if (!res.ok) return Error(res.statusText);
      return res.json();
    })
    .then((data) => {
      // Parse response and add to chat
      const { response } = data;
      messagesElement.appendChild(createMessageElement("Customer Service", marked.parse(response)));
    });
}

formElement.addEventListener("submit", handleSubmit);