// messages.js
const socket = io();

// Store current chat state
let currentRecipientId = null;
let currentSenderId = null;

function displayMessage(messageData) {
    const messageSpace = document.querySelector('.message-space');
    const messageBlock = document.createElement('div');
    messageBlock.className = `message-block ${messageData.sender_id === currentSenderId ? 'you' : 'other-person'}`;
    
    messageBlock.innerHTML = `
        <div class="message">
            <p>${messageData.message}</p>
            <span class="timestamp">${new Date(messageData.sent_time).toLocaleTimeString()}</span>
            
    `;
    
    messageSpace.appendChild(messageBlock);
    messageSpace.scrollTop = messageSpace.scrollHeight;
}

document.addEventListener("DOMContentLoaded", function () {
    const messageForm = document.querySelector('form');
    currentSenderId = document.querySelector('#receiver-id').value;
    currentRecipientId = document.querySelector('#sender-id').value;

    fetch(`/api/messages?sender_id=${currentSenderId}&receiver_id=${currentRecipientId}`)
        .then(response => {
            return response.json();
        })
        .then(messages => {
            messages.forEach(message => displayMessage(message));
        });
    
    if (messageForm) {
        messageForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // const messageInput = document.querySelector('#message');
            // const message = messageInput.value.trim();
            
            // if (message && currentRecipientId) {
            //     const messageData = {
            //         message: message,
            //         recepient_id: currentRecipientId,
            //         sender_id: currentSenderId
            //     };
                
            //     fetch('/api/messages', {
            //         method: 'POST',
            //         headers: {
            //             'Content-Type': 'application/json',
            //         },
            //         body: JSON.stringify(messageData)
            //     });
                
            //     messageInput.value = '';
            // }
        });
    }
    
    // Socket event listeners
    socket.on('connect', () => {
        console.log('Connected to Socket.IO server');
    });
    
    socket.on('receive_message', (data) => {
        const messageSpace = document.querySelector('.message-space');
        messageSpace.innerHTML = '';
        fetch(`/api/messages?sender_id=${currentSenderId}&receiver_id=${currentRecipientId}`)
        .then(response => {
            return response.json();
        })
        .then(messages => {
            messages.forEach(message => displayMessage(message));
        });
    });
});