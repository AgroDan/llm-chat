const messagesEl = document.getElementById('messages');
const form = document.getElementById('chat-form');
const input = document.getElementById('input');
const sendBtn = document.getElementById('send-btn');
const newChatBtn = document.getElementById('new-chat');

let messages = [];
let streaming = false;

function addMessageEl(role, text) {
  const div = document.createElement('div');
  div.className = `message ${role}`;
  div.textContent = text;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return div;
}

function scrollToBottom() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

async function sendMessage(text) {
  if (streaming || !text.trim()) return;
  streaming = true;
  sendBtn.disabled = true;

  messages.push({ role: 'user', content: text });
  addMessageEl('user', text);

  const assistantEl = addMessageEl('assistant', '');
  let assistantText = '';

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages }),
    });

    if (!res.ok) {
      assistantEl.remove();
      messages.pop(); // remove the user message we just pushed
      addMessageEl('error', `Server error (${res.status}). Check admin settings.`);
      streaming = false;
      sendBtn.disabled = false;
      return;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop();

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        const payload = JSON.parse(line.slice(6));

        if (payload.error) {
          assistantEl.remove();
          addMessageEl('error', payload.error);
          break;
        }
        if (payload.done) break;
        if (payload.content) {
          assistantText += payload.content;
          assistantEl.textContent = assistantText;
          scrollToBottom();
        }
      }
    }

    if (assistantText) {
      messages.push({ role: 'assistant', content: assistantText });
    } else {
      assistantEl.remove();
    }
  } catch (err) {
    assistantEl.remove();
    addMessageEl('error', 'Connection error: ' + err.message);
  }

  streaming = false;
  sendBtn.disabled = false;
  input.focus();
}

function submitInput() {
  const text = input.value;
  input.value = '';
  input.style.height = 'auto';
  sendMessage(text);
}

form.addEventListener('submit', (e) => {
  e.preventDefault();
  submitInput();
});

input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    submitInput();
  }
});

input.addEventListener('input', () => {
  input.style.height = 'auto';
  input.style.height = Math.min(input.scrollHeight, 120) + 'px';
});

newChatBtn.addEventListener('click', () => {
  messages = [];
  messagesEl.innerHTML = '';
  input.focus();
});
