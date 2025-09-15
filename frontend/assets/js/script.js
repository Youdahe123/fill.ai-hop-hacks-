// Dashboard State Management
let socket = null;
let isConnected = false;
let currentSessionId = null;
let uploadedFile = null;
let isConversationActive = false;
let selectedLanguage = 'en-US'; // Default language

// DOM Elements
const uploadSection = document.getElementById('uploadSection');
const processingSection = document.getElementById('processingSection');
const conversationSection = document.getElementById('conversationSection');
const resultsSection = document.getElementById('resultsSection');
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const statusIndicator = document.getElementById('statusIndicator');
const voiceIndicator = document.getElementById('voiceIndicator');
const processingMessage = document.getElementById('processingMessage');
const progressFill = document.getElementById('progressFill');
const progressFillSmall = document.getElementById('progressFillSmall');
const progressText = document.getElementById('progressText');
const progressPercent = document.getElementById('progressPercent');
const aiMessage = document.getElementById('aiMessage');
const aiMessageText = document.getElementById('aiMessageText');
const userMessage = document.getElementById('userMessage');
const userMessageText = document.getElementById('userMessageText');
const conversationStatus = document.getElementById('conversationStatus');
const speechOverlay = document.getElementById('speechOverlay');
const speechText = document.getElementById('speechText');
const generatedImage = document.getElementById('generatedImage');
const downloadBtn = document.getElementById('downloadBtn');
const newFormBtn = document.getElementById('newFormBtn');
const languageSelect = document.getElementById('languageSelect');

// Initialize
document.addEventListener('DOMContentLoaded', function () {
    console.log('🚀 Initializing Fill.ai frontend...');
    initializeWebSocket();
    initializeEventListeners();
});

// WebSocket Functions
function initializeWebSocket() {
    console.log('🔌 Initializing WebSocket connection...');

    // Check if Socket.IO is loaded
    if (typeof io === 'undefined') {
        console.error('❌ Socket.IO library not loaded!');
        updateStatus('error', 'Socket.IO not loaded');
        return;
    }

    console.log('✅ Socket.IO library loaded');

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${"localhost"}:5001`;

    console.log('🔗 Connecting to:', wsUrl);
    updateStatus('connecting', 'Connecting...');

    socket = io(wsUrl, {
        transports: ['websocket', 'polling'],
        timeout: 10000,
        forceNew: true
    });

    socket.on('connect', function () {
        console.log('✅ Connected to Fill.ai backend');
        isConnected = true;
        updateStatus('ready', 'Connected');
    });

    socket.on('disconnect', function () {
        console.log('❌ Disconnected from Fill.ai backend');
        isConnected = false;
        updateStatus('disconnected', 'Disconnected');
    });

    socket.on('connect_error', function (error) {
        console.error('❌ Connection error:', error);
        isConnected = false;
        updateStatus('error', 'Connection failed');
    });

    socket.on('connected', function (data) {
        console.log('Backend connected:', data.message);
    });

    socket.on('progress_update', function (data) {
        handleProgressUpdate(data);
    });

    socket.on('speech_text', function (data) {
        handleSpeechText(data);
    });

    socket.on('generated_image', function (data) {
        handleGeneratedImage(data);
    });

    socket.on('error', function (data) {
        handleError(data);
    });

    socket.on('processing_started', function (data) {
        console.log('Processing started:', data.message);
    });

    // Conversation event handlers
    socket.on('conversation_question', function (data) {
        handleConversationQuestion(data);
    });

    socket.on('conversation_answer', function (data) {
        handleConversationAnswer(data);
    });

    socket.on('conversation_complete', function (data) {
        handleConversationComplete(data);
    });

    // Voice event handlers
    socket.on('listening', function (data) {
        handleListening(data);
    });

    socket.on('user_speech', function (data) {
        handleUserSpeech(data);
    });

    socket.on('speech_timeout', function (data) {
        handleSpeechTimeout(data);
    });

    socket.on('speech_error', function (data) {
        handleSpeechError(data);
    });

    // Test connection after 2 seconds
    setTimeout(() => {
        if (!isConnected) {
            console.error('❌ Connection timeout - backend not responding');
            updateStatus('error', 'Backend not responding');
        }
    }, 2000);
}

function updateStatus(type, text) {
    console.log('📊 Status update:', type, text);
    if (statusIndicator) {
        statusIndicator.className = `status-indicator ${type}`;
        const span = statusIndicator.querySelector('span');
        if (span) {
            span.textContent = text;
        }
    }
}

// Progress and Speech Handling
function handleProgressUpdate(data) {
    console.log('Progress update:', data);

    if (data.step === 'starting') {
        showProcessingSection();
        updateStatus('processing', 'Processing');
    }

    updateProcessingMessage(data.message);

    if (data.progress !== null && data.progress !== undefined) {
        updateProgress(data.progress);
    }

    if (data.step === 'conversation') {
        showConversationSection();
        updateStatus('listening', 'Ready to Listen');
    }

    if (data.step === 'completed') {
        showResultsSection();
        updateStatus('ready', 'Completed');
    }
}

function handleSpeechText(data) {
    console.log('Speech text:', data);

    // Show speech overlay
    showSpeechOverlay(data.text);

    // Update conversation display
    updateAIMessage(data.text);

    // Update voice indicator
    if (voiceIndicator) {
        voiceIndicator.className = 'voice-indicator speaking';
        const span = voiceIndicator.querySelector('span');
        if (span) {
            span.textContent = 'Speaking';
        }
    }
}

function handleGeneratedImage(data) {
    console.log('Generated image:', data);

    // Check if we have image data
    if (data.image) {
        // Show the generated image
        if (generatedImage) {
            generatedImage.src = `data:image/png;base64,${data.image}`;
            generatedImage.alt = data.description || 'Generated form';

            // Show results section
            showResultsSection();

            // Enable download button
            if (downloadBtn) {
                downloadBtn.disabled = false;
            }

            console.log('✅ Image loaded successfully');
        }
    } else if (data.image_path) {
        // If we have a file path, we need to fetch it
        fetchGeneratedImage(data.image_path);
    } else {
        console.error('No image data provided');
        alert('Error: No image data received');
    }
}

async function fetchGeneratedImage(imagePath) {
    try {
        console.log('Fetching image from:', imagePath);

        // Convert the image to base64
        const response = await fetch(`http://localhost:5001/get_image?path=${encodeURIComponent(imagePath)}`);

        if (response.ok) {
            const blob = await response.blob();
            const reader = new FileReader();
            reader.onload = function () {
                const base64 = reader.result.split(',')[1];
                if (generatedImage) {
                    generatedImage.src = `data:image/png;base64,${base64}`;
                    generatedImage.alt = 'Generated form';
                    showResultsSection();
                    if (downloadBtn) {
                        downloadBtn.disabled = false;
                    }
                    console.log('✅ Image fetched and loaded successfully');
                }
            };
            reader.readAsDataURL(blob);
        } else {
            throw new Error('Failed to fetch image');
        }
    } catch (error) {
        console.error('Error fetching image:', error);
        alert('Error loading generated image. Please try again.');
    }
}

// Update the download function
function downloadGeneratedImage() {
    if (generatedImage && generatedImage.src && generatedImage.src !== '') {
        const link = document.createElement('a');
        link.href = generatedImage.src;
        link.download = 'filled-form.png';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        console.log('✅ Download started');
    } else {
        alert('No image available to download');
    }
}

// Add image load error handling
if (generatedImage) {
    generatedImage.addEventListener('error', function () {
        console.error('Failed to load generated image');
        alert('Failed to load the generated image. Please try again.');
    });
}

// Conversation handling
function handleConversationQuestion(data) {
    console.log('Conversation question:', data);

    // Update conversation display
    updateAIMessage(data.question);

    // Update progress
    if (data.progress) {
        updateConversationProgress(data.progress);
    }

    // Update conversation status
    if (conversationStatus) {
        conversationStatus.textContent = 'AI is asking a question...';
    }
}

function handleConversationAnswer(data) {
    console.log('Conversation answer:', data);

    // Show user's answer
    updateUserMessage(data.answer);

    // Show confirmation if confirmed
    if (data.confirmed) {
        setTimeout(() => {
            updateAIMessage(`Got it! ${data.field.label}: ${data.answer}`);
        }, 1000);
    }
}

function handleConversationComplete(data) {
    console.log('Conversation complete:', data);

    updateAIMessage(`Excellent! I've filled out ${data.filled_fields.length} fields. Now let me generate your completed form.`);
    if (conversationStatus) {
        conversationStatus.textContent = 'Generating your completed form...';
    }
}

// Voice handling
function handleListening(data) {
    console.log('Listening for voice input:', data);

    if (voiceIndicator) {
        voiceIndicator.className = 'voice-indicator listening';
        const span = voiceIndicator.querySelector('span');
        if (span) {
            span.textContent = 'Listening...';
        }
    }
    if (conversationStatus) {
        conversationStatus.textContent = 'Listening for your response...';
    }
}

function handleUserSpeech(data) {
    console.log('User speech detected:', data);

    // Show what the user said
    updateUserMessage(data.text);

    // Reset voice indicator
    if (voiceIndicator) {
        voiceIndicator.className = 'voice-indicator';
        const span = voiceIndicator.querySelector('span');
        if (span) {
            span.textContent = 'Ready';
        }
    }
}

function handleSpeechTimeout(data) {
    console.log('Speech timeout:', data);
    updateAIMessage("No speech detected. Please try again.");
    if (voiceIndicator) {
        voiceIndicator.className = 'voice-indicator';
        const span = voiceIndicator.querySelector('span');
        if (span) {
            span.textContent = 'Ready';
        }
    }
}

function handleSpeechError(data) {
    console.log('Speech error:', data);
    updateAIMessage(`Error: ${data.message}`);
    if (voiceIndicator) {
        voiceIndicator.className = 'voice-indicator';
        const span = voiceIndicator.querySelector('span');
        if (span) {
            span.textContent = 'Ready';
        }
    }
}

// UI Functions
function showUploadSection() {
    if (uploadSection) uploadSection.style.display = 'block';
    if (processingSection) processingSection.style.display = 'none';
    if (conversationSection) conversationSection.style.display = 'none';
    if (resultsSection) resultsSection.style.display = 'none';
}

function showProcessingSection() {
    if (uploadSection) uploadSection.style.display = 'none';
    if (processingSection) processingSection.style.display = 'block';
    if (conversationSection) conversationSection.style.display = 'none';
    if (resultsSection) resultsSection.style.display = 'none';
}

function showConversationSection() {
    if (uploadSection) uploadSection.style.display = 'none';
    if (processingSection) processingSection.style.display = 'none';
    if (conversationSection) conversationSection.style.display = 'block';
    if (resultsSection) resultsSection.style.display = 'none';
    isConversationActive = true;
}

function showResultsSection() {
    if (uploadSection) uploadSection.style.display = 'none';
    if (processingSection) processingSection.style.display = 'none';
    if (conversationSection) conversationSection.style.display = 'none';
    if (resultsSection) resultsSection.style.display = 'block';
    isConversationActive = false;

    // Ensure the image is visible
    if (generatedImage && generatedImage.src && generatedImage.src !== '') {
        generatedImage.style.display = 'block';
    }
}

function updateProcessingMessage(message) {
    if (processingMessage) {
        processingMessage.textContent = message;
    }
}

function updateProgress(progress) {
    if (progressFill) {
        progressFill.style.width = `${progress}%`;
    }
    if (progressFillSmall) {
        progressFillSmall.style.width = `${progress}%`;
    }
}

function updateConversationProgress(progress) {
    if (progressText) {
        progressText.textContent = `Question ${progress.current} of ${progress.total}`;
    }
    const percent = Math.round((progress.current / progress.total) * 100);
    if (progressPercent) {
        progressPercent.textContent = `${percent}%`;
    }
    if (progressFillSmall) {
        progressFillSmall.style.width = `${percent}%`;
    }
}

function updateAIMessage(text) {
    if (aiMessageText) {
        aiMessageText.textContent = text;
    }
    if (aiMessage) {
        aiMessage.style.display = 'flex';
    }
    if (userMessage) {
        userMessage.style.display = 'none';
    }
}

function updateUserMessage(text) {
    if (userMessageText) {
        userMessageText.textContent = text;
    }
    if (userMessage) {
        userMessage.style.display = 'flex';
    }
}

function showSpeechOverlay(text) {
    if (speechText) {
        speechText.textContent = text;
    }
    if (speechOverlay) {
        speechOverlay.style.display = 'block';

        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (speechOverlay) {
                speechOverlay.style.display = 'none';
            }
        }, 5000);
    }
}

// Event Listeners
function initializeEventListeners() {
    // File upload
    if (uploadArea) {
        uploadArea.addEventListener('click', () => {
            if (fileInput) {
                fileInput.click();
            }
        });

        uploadArea.addEventListener('dragover', handleDragOver);
        uploadArea.addEventListener('dragleave', handleDragLeave);
        uploadArea.addEventListener('drop', handleDrop);
    }

    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);
    }

    // Results actions
    if (downloadBtn) {
        downloadBtn.addEventListener('click', downloadGeneratedImage);
    }
    if (newFormBtn) {
        newFormBtn.addEventListener('click', startNewForm);
    }

    // Language selection
    if (languageSelect) {
        languageSelect.addEventListener('change', handleLanguageChange);
    }
}

// File Upload Functions
function handleDragOver(e) {
    e.preventDefault();
    if (uploadArea) {
        uploadArea.classList.add('dragover');
    }
}

function handleDragLeave(e) {
    e.preventDefault();
    if (uploadArea) {
        uploadArea.classList.remove('dragover');
    }
}

function handleDrop(e) {
    e.preventDefault();
    if (uploadArea) {
        uploadArea.classList.remove('dragover');
    }

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

function handleFile(file) {
    const allowedTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'];

    if (!allowedTypes.includes(file.type)) {
        alert('Please upload a PDF, JPEG, or PNG file.');
        return;
    }

    uploadedFile = file;

    // Upload file to backend
    uploadFileToBackend(file);
}

async function uploadFileToBackend(file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('http://localhost:5001/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.file_path) {
            // Update upload area
            if (uploadArea) {
                uploadArea.innerHTML = `
                    <div class="upload-icon">
                        <i class="fas fa-file-pdf" style="color: #ef4444;"></i>
                    </div>
                    <h3>${file.name}</h3>
                    <p>Ready to process</p>
                `;
            }

            // Start processing
            startProcessing(result.file_path);
        } else {
            throw new Error(result.error || 'Upload failed');
        }
    } catch (error) {
        console.error('Upload error:', error);
        alert('Failed to upload file. Please try again.');
    }
}

function startProcessing(filePath) {
    if (!isConnected) {
        alert('Not connected to backend. Please try again.');
        return;
    }

    // Start processing via WebSocket
    if (socket) {
        socket.emit('start_processing', {
            file_path: filePath,
            session_id: currentSessionId
        });
    }
}

function startNewForm() {
    // Reset everything
    uploadedFile = null;
    if (fileInput) {
        fileInput.value = '';
    }
    isConversationActive = false;

    // Reset upload area
    if (uploadArea) {
        uploadArea.innerHTML = `
            <div class="upload-icon">
                <i class="fas fa-cloud-upload-alt"></i>
            </div>
            <h3>Drop your file here</h3>
            <p>or <span class="upload-link">browse files</span></p>
        `;
    }

    // Show upload section
    showUploadSection();
    updateStatus('ready', 'Ready');
}

// Utility Functions
function generateSessionId() {
    return 'session_' + Math.random().toString(36).substr(2, 9);
}

// Initialize session ID
currentSessionId = generateSessionId();

// Add error handling
function handleError(data) {
    console.error('Error:', data);
    alert(`Error: ${data.message}`);
    showUploadSection();
    updateStatus('error', 'Error');
}

// Language Selection Functions
function handleLanguageChange(event) {
    selectedLanguage = event.target.value;
    console.log('🌐 Language changed to:', selectedLanguage);

    // Emit language change to backend if connected
    if (socket && isConnected) {
        socket.emit('language_changed', {
            language: selectedLanguage,
            session_id: currentSessionId
        });
    }

    // Update UI indicator
    const languageNames = {
        'en-US': 'English',
        'uk-UA': 'Ukrainian',
        'am-ET': 'Amharic'
    };

    console.log(`✅ AI will now recognize speech in ${languageNames[selectedLanguage]}`);
}

console.log('✅ Fill.ai frontend script loaded');
