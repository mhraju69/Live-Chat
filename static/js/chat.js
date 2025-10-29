// chat.js - WebSocket for chat functionality only
document.addEventListener("DOMContentLoaded", function() {
    // const roomId = "{{ room_id }}";
    const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
    const chatSocket = new WebSocket(`${wsScheme}://${window.location.host}/ws/chat/${roomId}/`);
    
    let lastSentMessage = '';

    // Chat WebSocket handlers
    chatSocket.onopen = () => console.log("Chat WebSocket connected");
    
    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        console.log("Got message:", data.message);

        // Skip if this is our own echoed message
        if(data.message === lastSentMessage) {
            return;
        }

        // Add received message to UI
        const messagesContainer = document.getElementById('messages-container');
        if (messagesContainer) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message received';
            messageDiv.innerHTML = `
                ${data.message} 
                <div class="message-time">${new Date().toLocaleTimeString()}</div>
            `;
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        // Update last message in chat list if available
        if (typeof updateLastMessageInList === 'function') {
            updateLastMessageInList(data.message, roomId);
        }
    };
    
    socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    if(data.type === 'notification') {
        // এখানে তুমি নোটিফিকেশন দেখাতে পারো
        alert(`New message from ${data.sender}: ${data.message}`);
        
        // অথবা ব্রাউজার নোটিফিকেশন API ব্যবহার করতে পারো
        if (Notification.permission === "granted") {
            new Notification(`Message from ${data.sender}`, {
                body: data.message,
                    // sound or other options
                });
            }
        }
    };

    chatSocket.onclose = () => console.log("Chat WebSocket closed");

    // Message sending function
    function sendMessage() {
        const input = document.getElementById('message-input');
        const message = input.value.trim();
        if (!message) return;

        lastSentMessage = message;
        chatSocket.send(JSON.stringify({message: message}));

        // Add sent message to UI
        const messagesContainer = document.getElementById('messages-container');
        if (messagesContainer) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message sent';
            messageDiv.innerHTML = `
                ${message} 
                <div class="message-time">${new Date().toLocaleTimeString()}</div>
            `;
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        input.value = '';
    }

    // Event listeners for sending messages
    const sendButton = document.getElementById('send-button');
    if (sendButton) {
        sendButton.onclick = sendMessage;
    }
    
    
    const messageInput = document.getElementById('message-input');
    if (messageInput) {
        messageInput.addEventListener('keypress', function(e) {
            if(e.key === 'Enter') sendMessage();
        });
    }

    // Initialize chat scroll position
    var chatMessages = document.getElementById("messages-container");
    if (chatMessages) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});