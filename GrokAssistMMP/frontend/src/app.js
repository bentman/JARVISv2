const { invoke } = window.__TAURI__.tauri;
const { listen } = window.__TAURI__.event;

document.getElementById('send').addEventListener('click', sendMessage);

document.getElementById('input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

async function sendMessage() {
    const input = document.getElementById('input');
    const query = input.value.trim();
    if (!query) return;
    appendMessage('user', query);
    input.value = '';
    try {
        const response = await fetch('http://localhost:8000/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query, conv_id: 0 })
        });
        const data = await response.json();
        appendMessage('ai', data.response);
    } catch (error) {
        appendMessage('ai', 'Error: ' + error);
    }
}

function appendMessage(sender, text) {
    const messages = document.getElementById('messages');
    const p = document.createElement('p');
    p.classList.add(sender === 'user' ? 'message-user' : 'message-ai');
    p.textContent = (sender === 'user' ? 'You: ' : 'AI: ') + text;
    messages.appendChild(p);
    messages.scrollTop = messages.scrollHeight;
}

document.getElementById('voice').addEventListener('click', () => {
    invoke('start_voice_loop').then(() => {
        document.getElementById('status').textContent = 'Voice mode started';
    }).catch((err) => {
        document.getElementById('status').textContent = 'Error starting voice: ' + err;
    });
});

document.getElementById('set-tier').addEventListener('click', () => {
    const tier = document.getElementById('tier-select').value;
    invoke('set_tier_to_backend', { tier }).then(() => {
        document.getElementById('status').textContent = 'Tier set to ' + tier;
    }).catch((err) => {
        document.getElementById('status').textContent = 'Error setting tier: ' + err;
    });
});

async function init() {
    try {
        const tier = await invoke('detect_tier');
        document.getElementById('tier-select').value = tier;
        document.getElementById('status').textContent = 'Detected tier: ' + tier;
    } catch (err) {
        document.getElementById('status').textContent = 'Error detecting tier: ' + err;
    }
}

listen('voice-response', (event) => {
    appendMessage('ai', event.payload.message);
});

init();