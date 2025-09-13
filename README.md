# Fill.ai - AI-Powered PDF Form Assistant

Fill.ai transforms static, confusing PDF forms into natural conversations, making form completion accessible for everyone, especially people with visual impairments.

## 🚀 Features

- **Conversational Form Filling**: Turn complex forms into natural back-and-forth conversations
- **Voice & Accessibility**: Voice input and text-to-speech output for accessibility
- **Smart AI Understanding**: AI understands context and validates responses
- **Real-time Processing**: WebSocket-based real-time updates and progress tracking
- **Multi-format Support**: Works with PDF, JPEG, and PNG files
- **Beautiful UI**: Modern, responsive interface with your custom logo

## 🏗️ Architecture

### Backend (Python/Flask)
- **WebSocket Server**: Real-time communication with frontend
- **File Upload API**: Handles PDF/image uploads
- **AI Integration**: OpenAI, Azure Computer Vision, ElevenLabs
- **Form Processing**: OCR, schema extraction, coordinate detection
- **Image Generation**: Creates filled forms with user data

### Frontend (HTML/CSS/JavaScript)
- **Responsive Design**: Works on desktop and mobile
- **Real-time Updates**: Live progress and speech display
- **Voice Recognition**: Built-in microphone support
- **File Upload**: Drag & drop or browse for files
- **Loading Screen**: Beautiful loading with your logo

## 📁 Project Structure

```
fill.ai/
├── backend/
│   ├── app.py                 # Main Flask WebSocket server
│   ├── server/
│   │   ├── websocket_workflow.py  # WebSocket-enabled form filler
│   │   ├── real_workflow.py       # Original workflow
│   │   ├── practice.py            # Schema extraction
│   │   ├── image_generator.py     # Form image generation
│   │   └── enhanced_coordinate_extractor.py
│   ├── uploads/               # File upload directory
│   ├── venv/                  # Python virtual environment
│   ├── .env                   # Environment variables (API keys)
│   └── start_backend.sh       # Backend startup script
├── frontend/
│   ├── index.html             # Main HTML file
│   ├── assets/
│   │   ├── css/style.css      # Styling
│   │   ├── js/script.js       # JavaScript functionality
│   │   └── images/            # Logo and assets
│   └── start_frontend.sh      # Frontend startup script
└── README.md
```

## 🛠️ Setup Instructions

### 1. Backend Setup

```bash
cd backend

# Activate virtual environment
source venv/bin/activate

# Install dependencies (if not already done)
pip install -r requirements.txt

# Add your API keys to .env file
nano .env
```

**Required API Keys in `.env`:**
```env
OPENAI_API_KEY=your_openai_api_key_here
AZURE_KEY=your_azure_key_here
AZURE_ENDPOINT=your_azure_endpoint_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
```

### 2. Start the Backend

```bash
# Option 1: Use the startup script
./start_backend.sh

# Option 2: Manual start
source venv/bin/activate
python3 app.py
```

The backend will run on `http://localhost:5000`

### 3. Start the Frontend

```bash
cd frontend

# Option 1: Use the startup script
./start_frontend.sh

# Option 2: Manual start
python3 -m http.server 3000
```

The frontend will run on `http://localhost:3000`

## 🎯 How to Use

1. **Open the Frontend**: Go to `http://localhost:3000`
2. **Upload a Form**: Click "Upload PDF Form" and select your PDF/image
3. **Watch the Magic**: 
   - Real-time progress updates
   - AI speech output displayed
   - Beautiful loading screen with your logo
4. **Get Results**: Download the filled form when complete

## 🔧 Technical Details

### WebSocket Events

**Backend → Frontend:**
- `progress_update`: Real-time progress updates
- `speech_text`: AI speech text to display
- `generated_image`: Completed form image
- `form_data`: Form schema and field data
- `error`: Error messages

**Frontend → Backend:**
- `start_processing`: Start form processing
- `send_message`: User messages during conversation

### API Endpoints

- `POST /upload`: Upload PDF/image files
- `GET /`: Health check endpoint

## 🎨 Customization

### Logo Integration
Your custom logo is integrated in:
- Header (40px)
- Footer (32px) 
- Loading screen (80px with animation)
- Real-time speech display

### Styling
- Purple gradient theme (`#853CFF` to `#A855F7`)
- Responsive design
- Smooth animations
- Accessibility features

## 🚨 Troubleshooting

### Common Issues

1. **"Not connected to backend"**
   - Make sure backend is running on port 5000
   - Check WebSocket connection in browser console

2. **"API key not found"**
   - Verify `.env` file has correct API keys
   - Restart backend after updating `.env`

3. **"Module not found"**
   - Make sure virtual environment is activated
   - Run `pip install -r requirements.txt`

4. **Audio not playing**
   - Install `mpv`: `brew install mpv` (macOS)
   - Check ElevenLabs API key

### Debug Mode

Backend runs in debug mode by default. Check console for detailed logs.

## 🔮 Future Enhancements

- [ ] User authentication
- [ ] Form templates library
- [ ] Batch processing
- [ ] Mobile app
- [ ] Advanced voice commands
- [ ] Multi-language support

## 📝 License

This project is part of the Fill.ai initiative to make forms accessible for everyone.

---

**Made with ❤️ for accessibility and ease of use**
