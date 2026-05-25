/**
 * Voice Assistant for PWD Assistant
 * Adds speech recognition (microphone) to the chatbot.
 * Works alongside existing TTS (voice output).
 */

(function() {
    // Check browser support for speech recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        console.warn("Speech Recognition not supported in this browser.");
        return;
    }

    let recognition = null;
    let isListening = false;

    // Function to inject microphone button into a given chat input container
    function addMicrophoneButton(chatInputContainer) {
        // If button already exists, skip
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
        `;

        // Find the send button to insert before it
        const sendButton = chatInputContainer.querySelector('button[type="button"], button.send-btn');
        if (sendButton) {
            chatInputContainer.insertBefore(micBtn, sendButton);
        } else {
            chatInputContainer.appendChild(micBtn);
        }

        // Setup speech recognition
        function initRecognition() {
            if (recognition) return;
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US'; // can be changed to 'hi-IN' for Hindi

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
                    // Trigger send action
                    const sendBtn = chatInputContainer.querySelector('button[type="button"], button.send-btn');
                    if (sendBtn) {
                        sendBtn.click();
                    } else {
                        // Simulate Enter key
                        const enterEvent = new KeyboardEvent('keypress', { key: 'Enter', bubbles: true });
                        inputField.dispatchEvent(enterEvent);
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
            if (isListening) {
                recognition.stop();
            } else {
                try {
                    recognition.start();
                } catch (e) {
                    console.warn(e);
                    // Re-initialize if needed
                    recognition = null;
                    initRecognition();
                    recognition.start();
                }
            }
        };
    }

    // Wait for DOM and then find all chatbot containers
    function initVoiceForAllChatbots() {
        // Look for chatbot containers (could be .chatbot-container or #chatbot-container)
        const chatbotContainers = document.querySelectorAll('.chatbot-container, #chatbot-container');
        chatbotContainers.forEach(container => {
            const chatInputArea = container.querySelector('.chat-input, .chat-input-container');
            if (chatInputArea && !chatInputArea.querySelector('.mic-btn')) {
                addMicrophoneButton(chatInputArea);
            }
        });
    }

    // Also watch for dynamically opened chatbots (if any)
    const observer = new MutationObserver(() => {
        initVoiceForAllChatbots();
    });
    observer.observe(document.body, { childList: true, subtree: true });

    // Run on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initVoiceForAllChatbots);
    } else {
        initVoiceForAllChatbots();
    }
})();