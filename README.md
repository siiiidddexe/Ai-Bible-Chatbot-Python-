# The-Bible-Ai-Python-Project [Open Source]

# 📖 Bible AI - Voice-Activated Spiritual Guide

A beautiful, modern voice-activated AI assistant that narrates Bible stories with cinematic detail. Features a stunning web interface with gradient orb animations and 100% voice control using macOS native speech.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.13-green)
![macOS](https://img.shields.io/badge/platform-macOS-lightgrey)

---

## ✨ Features

### 🎙️ **Voice Control**
- **Wake Word Activation**: Just say "Hey Bible" to activate
- **100% Voice-Only Interface**: No typing required
- **Interrupt Speech**: Click "Stop Speaking" to pause AI mid-sentence
- **macOS Native TTS**: Uses built-in `say` command for natural speech

### 🎨 **Beautiful Web Interface**
- **Ultra-Premium Design**: Gradient orb with breathing animations
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Real-Time Updates**: WebSocket communication for instant feedback
- **Dark Theme**: Easy on the eyes with purple/blue gradients

### 🤖 **AI-Powered Storytelling**
- **Google Gemini 2.5 Flash**: Latest AI model for biblical narratives
- **Cinematic Descriptions**: Vivid, immersive storytelling
- **Contextual Understanding**: Answers questions about biblical figures and events

### 🔑 **API Key Management**
- **First-Time Setup**: Beautiful modal for entering Gemini API key
- **Persistent Storage**: Saves key locally in JSON config
- **Easy Updates**: Click "🔑 Edit API Key" anytime to change
- **Secure**: Stored locally, never transmitted except to backend

---

## 🚀 Quick Start

### Prerequisites

- **macOS** (required for voice features)
- **Python 3.13** or higher
- **Google Gemini API Key** (free from [Google AI Studio](https://aistudio.google.com/app/apikey))
- **Microphone** for voice input

---

## 📥 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/bible-ai-chatbot.git
cd bible-ai-chatbot
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Required packages:**
- `google-generativeai==0.8.5` - Google Gemini AI SDK
- `SpeechRecognition==3.14.3` - Voice recognition with Python 3.13 support
- `websockets==15.0.1` - WebSocket server for web UI
- `audioop-lts` - Audio processing for Python 3.13

### Step 4: Get Your Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key (starts with `AIza...`)

---

## 🎬 Running the Application

### Option 1: Web Interface (Recommended)

```bash
python3 bible_ai_with_web.py
```

**What happens:**
- Backend server starts on `ws://localhost:8765`
- Web UI opens automatically in your default browser
- First-time users see API key setup modal
- Enter your Gemini API key and click "Save Key"
- Click "Start Listening" to begin

### Option 2: Standalone Desktop App

```bash
python3 bible_ai_app.py
```

**Features:**
- Traditional tkinter GUI window
- Same voice features as web version
- No browser required
- Gradient orb with animations

---

## 🎮 How to Use

### 1. **Start the App**
```bash
python3 bible_ai_with_web.py
```

### 2. **Setup API Key** (First Time Only)
- Modal appears automatically
- Enter your Gemini API key
- Click "Save Key"
- Key is saved to `bible_ai_config.json`

### 3. **Activate Voice Control**
- Click "**Start Listening**" button (turns red)
- Status shows "Listening for 'Hey Bible'..."

### 4. **Interact with Bible AI**
- Say: **"Hey Bible"**
- AI responds: "Yes, how can I help?"
- Ask your question or request a story
- AI responds with cinematic narration

### 5. **Interrupt Speech (NEW!)**
- While AI is speaking, button shows "**Stop Speaking**"
- Click to interrupt and resume listening
- AI stops immediately and waits for next "Hey Bible"

### 6. **Stop the AI**
- Click "**Stop**" button to deactivate completely
- Button turns blue and shows "Start Listening"

---

## 💡 Example Interactions

### Request Stories
```
You: "Hey Bible"
AI: "Yes, how can I help?"
You: "Tell me the story of David and Goliath"
AI: [Cinematic narration with vivid details...]
```

### Ask Questions
```
You: "Hey Bible"
AI: "Yes, how can I help?"
You: "Who was Moses?"
AI: [Clear, biblical explanation...]
```

### Request Specific Events
```
You: "Hey Bible"
AI: "Yes, how can I help?"
You: "Tell me about the crossing of the Red Sea"
AI: [Immersive, atmospheric description...]
```

---

## 📁 Project Structure

```
bible-ai-chatbot/
│
├── bible_ai_with_web.py      # Main web app (RECOMMENDED)
├── bible_ai_app.py            # Standalone desktop app
├── web_frontend.html          # Web UI with gradient orb
├── bible_ai_config.json       # API key storage (auto-created)
├── requirements.txt           # Python dependencies
├── README_NEW.md              # This file
└── .gitignore                 # Ignore config files
```

---

## ⚙️ Configuration

### API Key Storage (`bible_ai_config.json`)

Automatically created on first run:

```json
{
  "require_api_key_setup": false,
  "api_key": "AIza..."
}
```

**Important:** Add this to `.gitignore` to keep your API key private!

### Changing Your API Key

**Via Web UI:**
1. Click "🔑 Edit API Key" (top-right corner)
2. Enter new API key
3. Click "Save Key"

**Via Config File:**
1. Open `bible_ai_config.json`
2. Replace `api_key` value
3. Restart the app

---

## 🎨 Web UI Features

### Visual States

| State | Orb Animation | Status Color | Button |
|-------|---------------|--------------|--------|
| **Idle** | Gentle breathing | Gray | "Start Listening" (Blue) |
| **Listening** | Breathing | Green | "Stop" (Red) |
| **Speaking** | Dynamic waves | Blue | "Stop Speaking" (Red) |

### Responsive Design

- **Desktop (>768px)**: Full-size orb, wide layout
- **Tablet (768px)**: Medium orb, adjusted spacing
- **Mobile (<480px)**: Compact orb, stacked buttons

### Animations

- **Breathing Effect**: Smooth 4s ease-in-out infinite
- **Speaking Waves**: Rotating particles with pulsing glow
- **Sparkles**: Floating ✦ symbols with dynamic movement
- **Button Hovers**: Smooth color transitions

---

## 🔧 Troubleshooting

### "No module named 'google.generativeai'"
```bash
pip install --upgrade google-generativeai
```

### "No module named 'websockets'"
```bash
pip install websockets
```

### "Speech recognition not working"
```bash
pip install --upgrade SpeechRecognition audioop-lts
```

### "Port 8765 already in use"
```bash
# Kill existing Python processes
pkill -9 python3
# Then restart
python3 bible_ai_with_web.py
```

### "API Key configuration failed"
- Check your API key is correct (starts with `AIza...`)
- Ensure you have internet connection
- Try regenerating API key at [Google AI Studio](https://aistudio.google.com/app/apikey)

### "Microphone not working"
- Grant microphone permissions to Terminal/IDE in System Preferences
- macOS: System Preferences → Security & Privacy → Microphone
- Check your default microphone is selected

### "Stop Speaking doesn't work"
- Updated in v2.0 with subprocess control
- Uses `terminate()` and `kill()` for instant stopping
- Fallback with `killall say` for lingering processes

---

## 🔒 Security & Privacy

### API Key Storage
- Stored locally in `bible_ai_config.json`
- Never transmitted to third parties
- Add to `.gitignore` before committing

### Voice Data
- Processed via Google Speech Recognition API
- Audio sent to Google for transcription
- No local storage of voice recordings

### AI Responses
- Generated by Google Gemini API
- Sent over HTTPS to Google servers
- No local caching of responses

---

## 🛠️ Development

### Running in Development Mode

```bash
# Activate virtual environment
source venv/bin/activate

# Run with verbose output
python3 bible_ai_with_web.py

# Check WebSocket connection
# Browser console should show: "Connected to backend"
```

### Customizing the AI Persona

Edit the `system_instruction` in `bible_ai_with_web.py`:

```python
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction="""Your custom instructions here..."""
)
```

### Changing Wake Word

Modify the detection in `listen_and_process()`:

```python
if "hey bible" in text:  # Change "hey bible" to your wake word
```

---

## 📝 Requirements

### System Requirements
- macOS 10.14 or higher
- 4GB RAM minimum (8GB recommended)
- Internet connection for AI and speech recognition
- Microphone for voice input

### Python Packages
```txt
google-generativeai>=0.8.5
SpeechRecognition>=3.14.3
websockets>=15.0.1
audioop-lts
```

---

## 🚨 Known Issues

1. **Python 3.13 Compatibility**
   - Resolved: Using `SpeechRecognition==3.14.3` with `audioop-lts`

2. **WebSocket Handler**
   - Resolved: Updated to `websockets==15.0.1` API (removed `path` parameter)

3. **Speech Interruption**
   - Resolved: Switched from `os.system()` to `subprocess.Popen()` for proper process control

---

## 📄 License

This project is open source and available under the MIT License.

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📞 Support

Having issues? Try these steps:

1. Check [Troubleshooting](#-troubleshooting) section
2. Ensure all dependencies are installed
3. Verify your API key is valid
4. Check microphone permissions in System Preferences
5. Restart the application

---

## 🎯 Roadmap

### Upcoming Features
- [ ] Multiple language support
- [ ] Voice customization (speed, pitch, voice selection)
- [ ] Offline mode with local AI model
- [ ] Bible verse search and reference
- [ ] Daily devotional notifications
- [ ] Multi-user API key support
- [ ] Custom wake word configuration
- [ ] Speech-to-text history log
- [ ] Export conversations to PDF

---

## 🙏 Acknowledgments

- **Google Gemini AI** - Powering the biblical storytelling
- **Google Speech Recognition** - Voice transcription
- **macOS `say` command** - Natural text-to-speech
- **WebSockets** - Real-time web communication

---

## 📊 Version History

### v2.0.0 (Current)
- ✅ Added API key management modal
- ✅ Fixed "Stop Speaking" with subprocess control
- ✅ Enhanced responsive web design
- ✅ Added real-time WebSocket communication
- ✅ Improved error handling and logging

### v1.0.0
- Initial release with voice control
- Tkinter desktop interface
- Basic AI integration

---

## 📧 Contact

Questions or feedback? Open an issue on GitHub!

---

**Made with ❤️ for spiritual exploration through modern technology**

