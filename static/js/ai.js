// ============================================
// AssetFlow AI - AI Assistant JavaScript
// Chat and AI Interactions
// ============================================

let isProcessing = false;

// Send message to AI
function sendAIMessage() {
    const input = document.getElementById('aiInput') || document.getElementById('aiMessageInput');
    if (!input) return;
    
    const message = input.value.trim();
    if (!message || isProcessing) return;
    
    input.value = '';
    addMessage(message, 'user');
    
    showTypingIndicator();
    isProcessing = true;
    
    fetch('/ai/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        removeTypingIndicator();
        addMessage(data.response, 'ai');
        isProcessing = false;
    })
    .catch(error => {
        removeTypingIndicator();
        addMessage('Sorry, I encountered an error. Please try again.', 'ai');
        isProcessing = false;
        console.error('AI Error:', error);
    });
}

// Add message to chat
function addMessage(text, sender) {
    const container = document.getElementById('aiMessages') || document.getElementById('aiMessagesArea');
    if (!container) return;
    
    const div = document.createElement('div');
    div.className = `ai-message ${sender}`;
    
    const avatar = sender === 'ai' ? '🤖' : '👤';
    const content = text.split('\n').map(p => `<p>${p}</p>`).join('');
    
    div.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">${content}</div>
    `;
    
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

// Show typing indicator
function showTypingIndicator() {
    const container = document.getElementById('aiMessages') || document.getElementById('aiMessagesArea');
    if (!container) return;
    
    const indicator = document.createElement('div');
    indicator.className = 'ai-message ai';
    indicator.id = 'typingIndicator';
    indicator.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            <div class="typing-indicator">
                <span></span><span></span><span></span>
            </div>
        </div>
    `;
    container.appendChild(indicator);
    container.scrollTop = container.scrollHeight;
}

// Remove typing indicator
function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) indicator.remove();
}

// Ask AI from suggestion
function askAI(query) {
    const input = document.getElementById('aiInput') || document.getElementById('aiMessageInput');
    if (input) {
        input.value = query;
        sendAIMessage();
    }
}

// Clear chat
function clearChat() {
    const container = document.getElementById('aiMessages') || document.getElementById('aiMessagesArea');
    if (!container) return;
    
    container.innerHTML = `
        <div class="ai-message ai">
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                <p>Chat cleared! How can I help you with your assets today? 🚀</p>
            </div>
        </div>
    `;
}

// Enter key support
document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('aiInput') || document.getElementById('aiMessageInput');
    if (input) {
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendAIMessage();
            }
        });
    }
});

// Toggle AI Assistant (floating)
function toggleAIAssistant() {
    const chatWindow = document.getElementById('aiChatWindow');
    if (chatWindow) {
        chatWindow.classList.toggle('open');
    }
}

console.log('🤖 AI Assistant loaded successfully!');