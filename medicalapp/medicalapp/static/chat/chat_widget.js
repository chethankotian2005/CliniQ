document.addEventListener('DOMContentLoaded', function() {
    const toggle = document.getElementById('chat-toggle');
    const box = document.getElementById('chat-box');
    const close = document.getElementById('chat-close');
    const form = document.getElementById('chat-form');
    const input = document.getElementById('chat-input');
    const messages = document.getElementById('chat-messages');

    function openChat() {
        box.style.display = 'flex';
        box.setAttribute('aria-hidden', 'false');
        input.focus();
    }

    function closeChat() {
        box.style.display = 'none';
        box.setAttribute('aria-hidden', 'true');
        toggle.focus();
    }

    toggle.addEventListener('click', (e) => {
        e.stopPropagation();
        if (box.style.display === 'flex') closeChat(); else openChat();
    });

    close.addEventListener('click', (e) => { e.stopPropagation(); closeChat(); });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const text = input.value.trim();
        if (!text) return;
        appendMessage('user', text);
        input.value = '';
        appendMessage('system', 'Thinking...');

        try {
            const resp = await fetch('/chat/proxy/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });
            const data = await resp.json();
            // Replace last 'Thinking...' with real reply
            const lastSystem = messages.querySelector('.message.system:last-of-type');
            if (lastSystem) lastSystem.remove();
            appendMessage('bot', (data && data.reply) ? (typeof data.reply === 'string' ? data.reply : JSON.stringify(data.reply)) : 'No response');
        } catch (err) {
            const lastSystem = messages.querySelector('.message.system:last-of-type');
            if (lastSystem) lastSystem.remove();
            appendMessage('bot', 'Error contacting server');
        }
    });

    function appendMessage(type, text) {
        const el = document.createElement('div');
        el.className = `message ${type}`;
        el.textContent = text;
        messages.appendChild(el);
        messages.scrollTop = messages.scrollHeight;
    }

    // Close chat when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('#floating-chat')) {
            closeChat();
        }
    });
});
