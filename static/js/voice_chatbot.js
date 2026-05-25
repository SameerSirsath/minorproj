// ==================== VOICE OUTPUT (TTS) via Hugging Face ====================
let currentAudio = null;
let voiceEnabled = localStorage.getItem('pwdVoiceEnabled') !== 'false';
let audioUnlocked = false;

function unlockAudio() {
    if (audioUnlocked) return;
    audioUnlocked = true;
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (AudioContext) {
        const ctx = new AudioContext();
        if (ctx.state === 'suspended') {
            ctx.resume().catch(() => {});
        }
    }
}

async function speakText(text, lang = 'en') {
    if (!voiceEnabled || !text || !text.trim()) return;
    if (currentAudio) {
        currentAudio.pause();
        currentAudio = null;
    }
    try {
        const response = await fetch('/api/voice/speak', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text.trim() })
        });
        if (!response.ok) throw new Error('TTS failed');
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const audio = new Audio(url);
        currentAudio = audio;
        audio.onended = () => {
            URL.revokeObjectURL(url);
            currentAudio = null;
        };
        audio.onerror = () => {
            URL.revokeObjectURL(url);
            currentAudio = null;
        };
        if (!audioUnlocked) unlockAudio();
        await audio.play();
    } catch (e) {
        console.warn('TTS error:', e);
    }
}

function toggleVoice() {
    voiceEnabled = !voiceEnabled;
    localStorage.setItem('pwdVoiceEnabled', voiceEnabled);
    if (!voiceEnabled && currentAudio) currentAudio.pause();
    updateVoiceButtonUI();
}

function updateVoiceButtonUI() {
    const btn = document.getElementById('voice-toggle-btn');
    if (!btn) return;
    if (voiceEnabled) {
        btn.innerHTML = '<i class="fas fa-volume-up"></i>';
        btn.title = 'Voice ON — click to mute';
        btn.classList.remove('voice-muted');
    } else {
        btn.innerHTML = '<i class="fas fa-volume-mute"></i>';
        btn.title = 'Voice OFF — click to enable';
        btn.classList.add('voice-muted');
    }
}

// ==================== VOICE INPUT (Microphone) via Hugging Face ====================
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;

async function startRecording() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];
    mediaRecorder.ondataavailable = event => audioChunks.push(event.data);
    mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');
        
        // Show thinking state on mic button
        const micBtn = document.querySelector('.mic-btn');
        if (micBtn) {
            micBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            micBtn.disabled = true;
        }
        
        try {
            const response = await fetch('/api/voice/transcribe', {
                method: 'POST',
                body: formData
            });
            if (!response.ok) throw new Error('Transcription failed');
            const data = await response.json();
            const transcribedText = data.text;
            // Fill input and send
            const chatInput = document.getElementById('chat-input-field');
            if (chatInput) {
                chatInput.value = transcribedText;
                const sendBtn = document.querySelector('.chat-input button[type="button"]');
                if (sendBtn) sendBtn.click();
                else chatInput.dispatchEvent(new KeyboardEvent('keypress', { key: 'Enter', bubbles: true }));
            }
        } catch (e) {
            console.error('STT error:', e);
            alert('Could not transcribe audio. Please try again.');
        } finally {
            if (micBtn) {
                micBtn.innerHTML = '<i class="fas fa-microphone"></i>';
                micBtn.disabled = false;
                micBtn.style.background = '#007bff';
            }
            stream.getTracks().forEach(track => track.stop());
        }
    };
    mediaRecorder.start();
    isRecording = true;
}

function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
    }
}

function toggleRecording() {
    if (isRecording) {
        stopRecording();
        const micBtn = document.querySelector('.mic-btn');
        if (micBtn) {
            micBtn.innerHTML = '<i class="fas fa-microphone"></i>';
            micBtn.style.background = '#007bff';
        }
    } else {
        startRecording();
        const micBtn = document.querySelector('.mic-btn');
        if (micBtn) {
            micBtn.innerHTML = '<i class="fas fa-microphone-slash"></i>';
            micBtn.style.background = '#dc3545';
        }
    }
}

// Add microphone button to chat input
function addMicrophoneButton() {
    const chatInputContainer = document.querySelector('.chat-input');
    if (!chatInputContainer || chatInputContainer.querySelector('.mic-btn')) return;
    const micBtn = document.createElement('button');
    micBtn.type = 'button';
    micBtn.className = 'mic-btn';
    micBtn.innerHTML = '<i class="fas fa-microphone"></i>';
    micBtn.title = 'Click to speak your question';
    micBtn.style.cssText = `
        background: #007bff;
        color: white;
        border: none;
        border-radius: 50%;
        width: 44px;
        height: 44px;
        margin-left: 8px;
        cursor: pointer;
        font-size: 1.2rem;
        transition: all 0.2s ease;
        flex-shrink: 0;
    `;
    micBtn.onclick = toggleRecording;
    const sendButton = chatInputContainer.querySelector('button[type="button"]');
    if (sendButton) chatInputContainer.insertBefore(micBtn, sendButton);
    else chatInputContainer.appendChild(micBtn);
}

// ==================== CHATBOT CORE ====================
function setupChatbot() {
    const container = document.getElementById('chatbot-container');
    if (!container) return;
    const openBtn = document.getElementById('open-chatbot-btn');
    const closeBtn = document.getElementById('close-chatbot-btn');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input-field');
    const chatBody = document.getElementById('chat-body');
    const chatHeader = container.querySelector('.chat-header');
    
    if (!openBtn || !closeBtn || !chatForm) return;
    
    // Inject speaker toggle if missing
    if (chatHeader && !document.getElementById('voice-toggle-btn')) {
        const voiceBtn = document.createElement('button');
        voiceBtn.id = 'voice-toggle-btn';
        voiceBtn.className = 'voice-toggle-btn';
        voiceBtn.onclick = toggleVoice;
        chatHeader.insertBefore(voiceBtn, closeBtn);
        updateVoiceButtonUI();
    }
    
    openBtn.onclick = () => {
        container.style.display = 'flex';
        addMicrophoneButton();  // ensure mic button is added when opened
    };
    closeBtn.onclick = () => {
        container.style.display = 'none';
        if (currentAudio) currentAudio.pause();
        if (isRecording) stopRecording();
    };
    
    chatForm.onsubmit = (e) => {
        e.preventDefault();
        const message = chatInput.value.trim();
        if (!message) return;
        unlockAudio();
        addMessage(chatBody, 'user', message);
        chatInput.value = '';
        const typingId = showTypingIndicator(chatBody);
        setTimeout(() => {
            removeTypingIndicator(typingId);
            const reply = generateReply(message);
            addMessage(chatBody, 'bot', reply);
            speakText(reply);
        }, 800);
    };
}

function addMessage(chatBody, sender, text) {
    const div = document.createElement('div');
    div.className = `chat-message ${sender}-message`;
    div.innerHTML = `<p>${escapeHtml(text).replace(/\n/g, '<br>')}</p>`;
    chatBody.appendChild(div);
    chatBody.scrollTop = chatBody.scrollHeight;
}

function showTypingIndicator(chatBody) {
    const id = 'typing-' + Date.now();
    const div = document.createElement('div');
    div.id = id;
    div.className = 'chat-message bot-message typing-indicator';
    div.innerHTML = '<p><span></span><span></span><span></span></p>';
    chatBody.appendChild(div);
    chatBody.scrollTop = chatBody.scrollHeight;
    return id;
}

function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function generateReply(input) {
    const q = input.toLowerCase();
    if (q.includes('hello') || q.includes('hi')) return 'Hello! How can I assist you?';
    if (q.includes('scheme') || q.includes('benefit')) return 'You can find all government schemes in the Services Hub.';
    if (q.includes('reservation') || q.includes('job')) return 'Government jobs have 4% reservation for Persons with Disabilities.';
    if (q.includes('certificate') || q.includes('udid')) return 'UDID card is issued through the UDID portal. You need a disability certificate from a medical board.';
    if (q.includes('education') || q.includes('scholarship')) return 'There are many scholarships for PwD students. Check the National Scholarship Portal.';
    return 'I am still learning. Please ask about schemes, reservations, certificates, or education.';
}

function escapeHtml(str) {
    return str.replace(/[&<>]/g, function(m) {
        if (m === '&') return '&amp;';
        if (m === '<') return '&lt;';
        if (m === '>') return '&gt;';
        return m;
    });
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    setupChatbot();
    addMicrophoneButton();
    // Unlock autoplay on first user gesture
    const unlock = () => {
        if (window.AudioContext) new AudioContext().resume();
        document.removeEventListener('click', unlock);
        document.removeEventListener('touchstart', unlock);
    };
    document.addEventListener('click', unlock);
    document.addEventListener('touchstart', unlock);
});