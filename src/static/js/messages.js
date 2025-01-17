// messages.js
const socket = io();

// Store current chat state
let currentRecipientId = null;
let currentSenderId = null;

function displayMessage(messageData) {
	const messageSpace = document.querySelector(".message-space");
	const messageBlock = document.createElement("div");
	messageBlock.className = `message-block ${messageData.sender_id === currentSenderId ? "you" : "other-person"}`;
	messageBlock.id = messageData.id;

	messageBlock.innerHTML = `
	<form action="/community/messages/${messageData.receiver_id}/${messageData.id}" method="POST">
		<div class="message">
			<p>${messageData.message}</p>
			<span class="timestamp">Read status: ${messageData.is_read ? "Read" : "Unread"}</span>
			<button type="submit">Delete</button> 
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


function editMessage(form, id) {
	const message = document.querySelector(`#${id} .message p`).textContent;
	prompt("Enter the new content of your message.", message);
	
	
}