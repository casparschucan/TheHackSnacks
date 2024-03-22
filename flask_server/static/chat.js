
const chatContainer = document.getElementById('chat-container');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');


var session_id = null;

function sendMessage(message, first_message=false) {
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
  //await this thingy
  fetch('/api/chat_message/', {
    method: 'POST',
    headers: new Headers({'content-type': 'application/json'}),
    body: JSON.stringify(
        { 
            "message": message,
            "session_id": session_id ,
            "first_message": first_message,
        }),
  })
    .then(response => response.json())
    .then(data => handleUserResponse(data))
}

sendButton.addEventListener('click', () => {
  const message = messageInput.value.trim();
  if (message) {
    //check if session_id exists
    if (typeof(session_id) == 'undefined'){
        session_id = null;
    }

    console.log(session_id);
    sendMessage(message,false);
  }
});

// Handle pressing Enter in the input field
messageInput.addEventListener('keyup', (event) => {
  if (event.key === 'Enter') {
    sendButton.click();
  }
});

// Handle response by user
function handleUserResponse(response) {
    let responseText = response.message;
    session_id = response.session_id;
    const chatbotMessage = document.createElement('div');
    chatbotMessage.classList.add('chat-message', 'chatbot');
    chatbotMessage.textContent = responseText;
    chatContainer.appendChild(chatbotMessage);
}

// Send a welcome message when the page loads
sendMessage("", true);