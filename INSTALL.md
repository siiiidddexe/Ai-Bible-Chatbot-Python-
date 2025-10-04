# 🚀 Quick Installation Guide

## One-Line Setup

```bash
# Clone and setup
git clone hhttps://github.com/siiiidddexe/The-Bible-Ai-Python-Project.git
cd bible-ai-chatbot
./start.sh
```

That's it! The script will:
- ✅ Check Python installation
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Start the web application
- ✅ Open browser automatically

---

## Manual Setup (If Preferred)

### 1. Clone Repository
```bash
git clone hhttps://github.com/siiiidddexe/The-Bible-Ai-Python-Project.git
cd bible-ai-chatbot
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run Application
```bash
python3 bible_ai_with_web.py
```

---

## 🔑 Get Your API Key

1. Visit: https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key (starts with `AIza...`)
5. Enter in the modal when app starts

---

## 📱 Usage

1. **Click "Start Listening"** (button turns red)
2. **Say "Hey Bible"** (wake word)
3. **Ask your question** after AI responds
4. **Click "Stop Speaking"** to interrupt AI anytime
5. **Click "Stop"** to deactivate completely

---

## 🔧 Troubleshooting

### Dependencies Issue
```bash
pip install --upgrade google-generativeai SpeechRecognition websockets audioop-lts
```

### Port Already in Use
```bash
pkill -9 python3
python3 bible_ai_with_web.py
```

### Microphone Not Working
- System Preferences → Security & Privacy → Microphone
- Enable access for Terminal or your IDE

---

## 📚 Full Documentation

See [README_NEW.md](README_NEW.md) for complete documentation.

---

**Questions?** Open an issue on GitHub!
