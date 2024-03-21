
const chatContainer = document.getElementById('chat-container');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');

function sendMessage(message, session_id=null) {
  // Create a message element for the user
  const userMessage = document.createElement('div');
  userMessage.classList.add('chat-message', 'user');
  userMessage.textContent = message;
  chatContainer.appendChild(userMessage);

  // Clear the input field
  messageInput.value = '';

  // Function to handle the chatbot response
  function handleResponse(responseText) {
    const chatbotMessage = document.createElement('div');
    chatbotMessage.classList.add('chat-message', 'chatbot');
    chatbotMessage.textContent = responseText;
    chatContainer.appendChild(chatbotMessage);
  }

  // Send the user message to the REST API
  fetch('/api/chat_message/', {
    method: 'POST',
    headers: new Headers({'content-type': 'application/json'}),
    body: JSON.stringify({ "message": message, "session_id": session_id }),
  })
    .then(response => response.json())
    .then(data => handleResponse(data.response));
}

sendButton.addEventListener('click', () => {
  const message = messageInput.value.trim();
  if (message) {
    sendMessage(message);
  }
});

// Handle pressing Enter in the input field
messageInput.addEventListener('keyup', (event) => {
  if (event.key === 'Enter') {
    sendButton.click();
  }
});
