import { renderMarkdown } from "./markdown";
import { toast } from "./toast";

type Message = { role: "bot" | "user"; content: string };

const messagesElement = document.getElementById("messages");
const formElement = document.getElementById("form");
if (!messagesElement || !(formElement instanceof HTMLFormElement)) throw new Error("Missing chat elements.");

const messages: Message[] = [{ role: "bot", content: "Hello! How can I help you today?" }];

function renderMessages() {
  if (!messagesElement) return;
  messagesElement.replaceChildren();

  for (const { role, content } of messages) {
    const card = document.createElement("div");
    card.classList.add("container", "card");
    const cardBody = document.createElement("div");
    cardBody.classList.add("card-body");
    const cardTitle = document.createElement("h5");
    cardTitle.classList.add("card-title");
    cardTitle.textContent = role === "bot" ? "Eco Bot" : "You";
    const cardText = document.createElement("div");
    cardText.classList.add("card-text");
    cardText.innerHTML = renderMarkdown(content);
    cardBody.append(cardTitle, cardText);
    card.appendChild(cardBody);
    messagesElement.appendChild(card);
  }

  messagesElement.scrollTop = messagesElement.scrollHeight;
}

formElement.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!(formElement instanceof HTMLFormElement)) return;
  const content = new FormData(formElement).get("content");
  if (typeof content !== "string" || !content.trim()) {
    toast("Please enter a message!", "danger");
    return;
  }

  const history = [...messages];
  formElement.reset();
  messages.push({ role: "user", content });
  renderMessages();

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: content, history }),
    });
    if (!response.ok) throw new Error(`Chat request failed: ${response.status}`);
    const data: unknown = await response.json();
    if (typeof data !== "object" || data === null || !("response" in data) || typeof data.response !== "string")
      throw new Error("Invalid chat response.");
    messages.push({ role: "bot", content: data.response });
  } catch (error) {
    console.error(error);
    toast("Unable to send the message. Please try again.", "danger");
  } finally {
    renderMessages();
  }
});

renderMessages();
