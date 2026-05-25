/**
 * PWD Assistant - Complete JS with Voice Input + Output
 * 
 * Features:
 * - Voice input (microphone) using Web Speech API
 * - Voice output (speaker) using backend /api/tts (gTTS)
 * - Works with existing chatbot HTML (IDs: chatbot-container, chat-form, etc.)
 * - No changes to HTML structure required
 */

// ─────────────────────────────────────────────────────────────────────────────
// VOICE OUTPUT (Text-to-Speech)
// ─────────────────────────────────────────────────────────────────────────────

let currentAudio = null;
let voiceEnabled = localStorage.getItem('pwdVoiceEnabled') !== 'false'; // default ON

/**
 * Call the backend TTS endpoint and play the returned MP3.
 */
async function speakText(text, lang = 'en') {
    if (!voiceEnabled || !text || !text.trim()) {
        console.log('[TTS] Skipped: voice disabled or empty text');
        return;
    }

    if (currentAudio) {
        currentAudio.pause();
        currentAudio = null;
    }

    try {
        const response = await fetch('/api/tts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text.trim(), lang })
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error(`[TTS] Server error (${response.status}):`, errorText);
            return;
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const audio = new Audio(url);
        currentAudio = audio;

        audio.onended = () => {
            URL.revokeObjectURL(url);
            currentAudio = null;
        };
        audio.onerror = (e) => {
            console.error('[TTS] Audio playback error:', e);
            URL.revokeObjectURL(url);
            currentAudio = null;
        };

        await audio.play();
    } catch (err) {
        console.error('[TTS] Fetch or play error:', err);
    }
}

/**
 * Toggle voice output on/off and update UI.
 */
function toggleVoice() {
    voiceEnabled = !voiceEnabled;
    localStorage.setItem('pwdVoiceEnabled', voiceEnabled);
    if (!voiceEnabled && currentAudio) {
        currentAudio.pause();
        currentAudio = null;
    }
    updateVoiceButtonUI();
}

/**
 * Update the speaker button icon based on voiceEnabled state.
 */
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

// ─────────────────────────────────────────────────────────────────────────────
// VOICE INPUT (Speech Recognition / Microphone)
// ─────────────────────────────────────────────────────────────────────────────

let recognition = null;
let isListening = false;

/**
 * Inject a microphone button into the chat input area.
 * This function is called for each chatbot container.
 */
function addMicrophoneButton(chatInputContainer) {
    if (chatInputContainer.querySelector('.mic-btn')) return;

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

    // Insert before the send button (or append if not found)
    const sendButton = chatInputContainer.querySelector('button[type="button"], button.send-btn, #send-message-btn');
    if (sendButton) {
        chatInputContainer.insertBefore(micBtn, sendButton);
    } else {
        chatInputContainer.appendChild(micBtn);
    }

    function initRecognition() {
        if (recognition) return;

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            console.warn("Speech Recognition not supported in this browser.");
            micBtn.disabled = true;
            micBtn.title = "Speech recognition not supported";
            return;
        }

        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US'; // Change to 'hi-IN' for Hindi

        recognition.onstart = () => {
            isListening = true;
            micBtn.innerHTML = '<i class="fas fa-microphone-slash"></i>';
            micBtn.style.background = '#dc3545';
        };

        recognition.onend = () => {
            isListening = false;
            micBtn.innerHTML = '<i class="fas fa-microphone"></i>';
            micBtn.style.background = '#007bff';
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            const inputField = chatInputContainer.querySelector('input[type="text"], input[type="search"]');
            if (inputField) {
                inputField.value = transcript;
                // Trigger send
                const sendBtn = chatInputContainer.querySelector('button[type="button"], button.send-btn, #send-message-btn');
                if (sendBtn) {
                    sendBtn.click();
                } else {
                    inputField.dispatchEvent(new KeyboardEvent('keypress', { key: 'Enter', bubbles: true }));
                }
            }
        };

        recognition.onerror = (event) => {
            console.error("Speech recognition error", event.error);
            isListening = false;
            micBtn.innerHTML = '<i class="fas fa-microphone"></i>';
            micBtn.style.background = '#007bff';
            if (event.error === 'not-allowed') {
                alert("Microphone access denied. Please allow microphone to use voice input.");
            }
        };
    }

    micBtn.onclick = () => {
        if (!recognition) initRecognition();
        if (!recognition) return;
        if (isListening) {
            recognition.stop();
        } else {
            try {
                recognition.start();
            } catch (e) {
                console.warn(e);
                recognition = null;
                initRecognition();
                if (recognition) recognition.start();
            }
        }
    };
}

/**
 * Find all chatbot containers and add microphone buttons.
 * Runs on page load and watches for dynamically added chatbots.
 */
function initVoiceInputForAllChatbots() {
    const chatbotContainers = document.querySelectorAll('.chatbot-container, #chatbot-container');
    chatbotContainers.forEach(container => {
        const chatInputArea = container.querySelector('.chat-input, .chat-input-container');
        if (chatInputArea && !chatInputArea.querySelector('.mic-btn')) {
            addMicrophoneButton(chatInputArea);
        }
    });
}

// Watch for dynamically added chatbots (modals, late rendering)
const observer = new MutationObserver(() => {
    initVoiceInputForAllChatbots();
});
observer.observe(document.body, { childList: true, subtree: true });

// ─────────────────────────────────────────────────────────────────────────────
// SERVICES HUB (planner.html) – unchanged
// ─────────────────────────────────────────────────────────────────────────────

function searchResources() {
    const domain = document.getElementById('domain');
    const location = document.getElementById('location');
    const resultDiv = document.getElementById('planResult');
    if (!domain || !location || !resultDiv) return;

    const domainVal = domain.value;
    const locationVal = location.value.trim();

    if (!domainVal || !locationVal) {
        resultDiv.innerHTML = `<div class="card" style="text-align:center;color:#c62828;background:#ffebee;padding:20px;"><strong>Please complete all fields to perform a search.</strong></div>`;
        resultDiv.style.display = 'block';
        return;
    }

    resultDiv.innerHTML = `<div class="result-header"><h2>Displaying mock results for ${domainVal} in ${locationVal}</h2></div>`;
    resultDiv.style.display = 'block';
    resultDiv.scrollIntoView({ behavior: 'smooth' });
}

// ─────────────────────────────────────────────────────────────────────────────
// VIDEO GUIDE (guide.html) – unchanged
// ─────────────────────────────────────────────────────────────────────────────

function searchVideos(query) {
    const searchInput = document.getElementById('searchInput');
    const videoContainer = document.getElementById('videoContainer');
    const searchTerm = query || (searchInput ? searchInput.value.trim() : '');
    if (!searchTerm) {
        alert('Please enter a search topic.');
        return;
    }
    if (videoContainer) {
        videoContainer.innerHTML = `<p style="text-align:center;padding:20px;">Showing mock video results for "${searchTerm}"...</p>`;
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// CHATBOT CORE – with voice input + output
// ─────────────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    const openChatbotBtn = document.getElementById('open-chatbot-btn');
    const chatbotContainer = document.getElementById('chatbot-container');
    const closeChatbotBtn = document.getElementById('close-chatbot-btn');
    const chatForm = document.getElementById('chat-form');
    const chatInputField = document.getElementById('chat-input-field');
    const chatBody = document.getElementById('chat-body');
    const chatHeader = document.querySelector('.chat-header');

    if (!openChatbotBtn || !chatbotContainer || !closeChatbotBtn || !chatForm) return;

    // Inject voice toggle button (speaker) into chat header
    if (chatHeader && !document.getElementById('voice-toggle-btn')) {
        const voiceBtn = document.createElement('button');
        voiceBtn.id = 'voice-toggle-btn';
        voiceBtn.className = 'voice-toggle-btn';
        voiceBtn.onclick = toggleVoice;
        chatHeader.insertBefore(voiceBtn, closeChatbotBtn);
        updateVoiceButtonUI();
    }

    // Open chatbot
    openChatbotBtn.addEventListener('click', () => {
        chatbotContainer.style.display = 'flex';
        initVoiceInputForAllChatbots();
    });

    // Close chatbot
    closeChatbotBtn.addEventListener('click', () => {
        chatbotContainer.style.display = 'none';
        if (currentAudio) currentAudio.pause();
    });

    // Send message handler
    chatForm.addEventListener('submit', (event) => {
        event.preventDefault();
        const userMessage = chatInputField.value.trim();
        if (!userMessage) return;

        addMessageToChat('user', userMessage);
        chatInputField.value = '';

        const typingId = showTypingIndicator();

        setTimeout(() => {
            removeTypingIndicator(typingId);
            const botResponse = generateBotResponse(userMessage);
            addMessageToChat('bot', botResponse);
            speakText(botResponse);   // Voice output
        }, 1000);
    });

    // Helper: add a message bubble
    function addMessageToChat(sender, message) {
        if (!chatBody) return;
        const wrapper = document.createElement('div');
        wrapper.className = `chat-message ${sender}-message`;
        const safeMessage = message.replace(/[&<>]/g, (m) => {
            if (m === '&') return '&amp;';
            if (m === '<') return '&lt;';
            if (m === '>') return '&gt;';
            return m;
        }).replace(/\n/g, '<br>');
        wrapper.innerHTML = `<p>${safeMessage}</p>`;
        chatBody.appendChild(wrapper);
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    // Typing indicator
    function showTypingIndicator() {
        const id = 'typing-' + Date.now();
        const wrapper = document.createElement('div');
        wrapper.id = id;
        wrapper.className = 'chat-message bot-message typing-indicator';
        wrapper.innerHTML = '<p><span></span><span></span><span></span></p>';
        chatBody.appendChild(wrapper);
        chatBody.scrollTop = chatBody.scrollHeight;
        return id;
    }

    function removeTypingIndicator(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    // Simple rule‑based response generator (enhanced)
    function generateBotResponse(userInput) {
        const input = userInput.toLowerCase();
        if (input.includes('hello') || input.includes('hi')) return 'Hello there! How can I assist you today?';
        if (input.includes('scheme') || input.includes('pension')) return 'You can find detailed information on government schemes in our "Services Hub".';
        if (input.includes('help') || input.includes('support')) return 'I am here to help. You can ask me about services, resources, or the community forum.';
        if (input.includes('thank')) return "You're welcome! Is there anything else I can help with?";
        if (input.includes('reservation') || input.includes('job')) return 'Under the RPwD Act 2016, 4% of government jobs are reserved for Persons with Disabilities.';
        if (input.includes('certificate') || input.includes('udid')) return 'A UDID (Unique Disability ID) card is issued by the government. Visit the UDID portal to apply online.';
        if (input.includes('education') || input.includes('scholarship')) return 'Various scholarships are available for PwD students. Check the National Scholarship Portal for details.';
        return "I'm sorry, I'm still learning. Try asking about 'schemes', 'reservation', 'certificate', or 'help'.";
    }

    // Initial injection
    initVoiceInputForAllChatbots();

    // Unlock autoplay on first user gesture (required by some browsers)
    const unlockAudio = () => {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        if (ctx.state === 'suspended') ctx.resume();
        document.removeEventListener('click', unlockAudio);
        document.removeEventListener('touchstart', unlockAudio);
    };
    document.addEventListener('click', unlockAudio);
    document.addEventListener('touchstart', unlockAudio);
});