import os
import sys

# Suppress all warnings and gRPC logs - MUST be set FIRST before any other imports
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GRPC_TRACE'] = ''
os.environ['GRPC_VERBOSITY'] = 'NONE'
os.environ['GLOG_minloglevel'] = '3'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Redirect stderr to devnull to suppress C++ library warnings
import io
_original_stderr = sys.stderr
sys.stderr = open(os.devnull, 'w')

import threading
import time
import warnings
import math
import random
import webbrowser
import asyncio
import json
import subprocess
import signal
from pathlib import Path
warnings.filterwarnings('ignore')

import tkinter as tk
from tkinter import scrolledtext
import google.generativeai as genai
import speech_recognition as sr

# WebSocket server for communication with web frontend
try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    print("Installing websockets library...")
    os.system(f"{sys.executable} -m pip install websockets")
    import websockets
    WEBSOCKETS_AVAILABLE = True

# Restore stderr after all imports are complete
sys.stderr.close()
sys.stderr = _original_stderr

# --- Configuration ---
CONFIG_FILE = Path(__file__).parent / "bible_ai_config.json"
DEFAULT_API_KEY = ""

# Load or create configuration
def load_config():
    """Load configuration from JSON file"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"require_api_key_setup": True, "api_key": ""}

def save_config(config):
    """Save configuration to JSON file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Failed to save config: {e}")
        return False

# Load config
config = load_config()

# Use stored API key or default
if config.get("require_api_key_setup") and not config.get("api_key"):
    YOUR_API_KEY = DEFAULT_API_KEY
else:
    YOUR_API_KEY = config.get("api_key", DEFAULT_API_KEY)

# Configure the Gemini API client
model = None

def configure_gemini(api_key):
    """Configure Gemini API with the given key"""
    global model
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction="""You are the Bible AI, a wise and eloquent storyteller. Your purpose is to narrate stories and concepts from the Bible. 
            When asked for a story, you must tell it in a cinematic, descriptive, and immersive way. 
            Use vivid imagery, describe the scenes, the emotions of the characters, and the atmosphere. 
            Speak in a clear, calm, and respectful tone. Your goal is to make the listener feel like they are there.
            Keep your responses focused on the user's request.
            If the user asks a question that is not about a story (e.g., 'who was Moses?'), answer it clearly and concisely from a biblical perspective.
            Begin your stories directly without introductory phrases like 'Of course, here is a story...'
            """
        )
        return True
    except Exception as e:
        print(f"API Key configuration failed: {e}")
        return False

# Initial configuration
configure_gemini(YOUR_API_KEY)

# Global WebSocket clients
websocket_clients = set()
say_process = None  # Store the current say process

async def broadcast_to_web(message):
    """Send message to all connected web clients"""
    if websocket_clients:
        await asyncio.gather(
            *[client.send(json.dumps(message)) for client in websocket_clients],
            return_exceptions=True
        )

def broadcast_sync(message):
    """Synchronous wrapper for broadcasting"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(broadcast_to_web(message))
        loop.close()
    except:
        pass

# --- Core Functions ---

def speak(text):
    """Uses macOS's built-in 'say' command to speak text aloud with animation."""
    global say_process
    
    update_status("Speaking...", "speaking")
    app.is_speaking = True
    app.start_speaking_animation()
    
    # Update button to show 'Stop Speaking'
    app.toggle_button.config(text="Stop Speaking", bg="#ff4757", activebackground="#ee3344", fg="#ffffff")
    broadcast_sync({"type": "button", "text": "Stop Speaking", "color": "red"})
    
    # Write text to a temporary file to avoid shell escaping issues with long text
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(text)
        temp_file = f.name
    
    try:
        # Use subprocess instead of os.system for better control
        say_process = subprocess.Popen(['say', '-f', temp_file])
        say_process.wait()  # Wait for completion
    except Exception as e:
        print(f"Speech error: {e}")
    finally:
        say_process = None
        # Clean up temp file
        try:
            os.remove(temp_file)
        except:
            pass
    
    app.is_speaking = False
    app.stop_speaking_animation()
    
    # Only update if still listening (not manually stopped)
    if is_listening:
        app.toggle_button.config(text="Stop", bg="#ff4757", activebackground="#ee3344", fg="#ffffff")
        broadcast_sync({"type": "button", "text": "Stop", "color": "red"})
        update_status("Listening for 'Hey Bible'...", "listening")

def listen_and_process():
    """The main loop for listening for the wake word and commands."""
    global is_listening
    recognizer = sr.Recognizer()

    while is_listening:
        try:
            # Don't listen while speaking
            if app.is_speaking:
                time.sleep(0.1)
                continue
                
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                update_status("Listening for 'Hey Bible'...", "listening")
                app.set_listening_state()
                
                audio_wake_word = recognizer.listen(source, phrase_time_limit=10)
            
            text = recognizer.recognize_google(audio_wake_word).lower()
            log_message(f"Heard: {text}")

            if "hey bible" in text:
                update_status("Wake word detected. Listening for your command...", "processing")
                app.set_processing_state()
                speak("Yes, how can I help?")
                
                # Wait for the prompt after wake word
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    update_status("Listening for command...", "listening")
                    audio_command = recognizer.listen(source, timeout=5, phrase_time_limit=15)
                
                prompt = recognizer.recognize_google(audio_command)
                log_message(f"User Prompt: {prompt}")

                update_status("Thinking...", "thinking")
                app.set_thinking_state()

                response = model.generate_content(prompt)
                response_text = response.text
                log_message(f"AI Response: {response_text}\n")
                speak(response_text)

        except sr.WaitTimeoutError:
            if "wake word detected" in app.status_label.cget("text").lower():
                log_message("No command heard after wake word.")
                speak("I'm sorry, I didn't hear a command.")
            continue
        except sr.UnknownValueError:
            continue
        except sr.RequestError as e:
            log_message(f"Could not request results; {e}")
            speak("There seems to be an issue with the speech recognition service.")
            time.sleep(2)
        except Exception as e:
            log_message(f"An unexpected error occurred: {e}")
            time.sleep(2)

# --- GUI Functions ---

def update_status(message, state="idle"):
    """Update status in both tkinter and web UI"""
    app.status_label.config(text=message)
    broadcast_sync({"type": "status", "message": message, "state": state})

def log_message(message):
    """Log message in both tkinter and web UI"""
    app.log_area.config(state=tk.NORMAL)
    app.log_area.insert(tk.END, message + "\n")
    app.log_area.see(tk.END)
    app.log_area.config(state=tk.DISABLED)
    broadcast_sync({"type": "log", "message": message})

def toggle_listening():
    global is_listening, listening_thread, say_process
    
    # If speaking, stop it and resume listening
    if app.is_speaking:
        # Kill the say process if it exists
        if say_process and say_process.poll() is None:
            say_process.terminate()
            try:
                say_process.wait(timeout=0.5)
            except subprocess.TimeoutExpired:
                say_process.kill()
        
        # Also kill any lingering say processes
        try:
            subprocess.run(['killall', 'say'], check=False)
        except:
            pass
        
        app.is_speaking = False
        app.stop_speaking_animation()
        log_message("Speech interrupted by user")
        
        # Resume listening mode (don't stop the listening thread)
        app.toggle_button.config(text="Stop", bg="#ff4757", activebackground="#ee3344", fg="#ffffff")
        update_status("Listening for 'Hey Bible'...", "listening")
        app.status_label.config(fg="#10b981")
        broadcast_sync({"type": "button", "text": "Stop", "color": "red"})
        return
    
    # If listening, stop it
    if is_listening:
        is_listening = False
        app.toggle_button.config(text="Start Listening", bg="#6366f1", activebackground="#5b5ff1", fg="#f0f0f0")
        update_status("Ready", "idle")
        app.status_label.config(fg="#9ca3af")
        log_message("--- AI Deactivated ---\n")
        broadcast_sync({"type": "button", "text": "Start Listening", "color": "blue"})
        app.set_idle_state()
    else:
        # Start listening
        is_listening = True
        listening_thread = threading.Thread(target=listen_and_process, daemon=True)
        listening_thread.start()
        app.toggle_button.config(text="Stop", bg="#ff4757", activebackground="#ee3344", fg="#ffffff")
        log_message("--- AI Activated ---")
        update_status("Listening...", "listening")
        app.status_label.config(fg="#10b981")
        broadcast_sync({"type": "button", "text": "Stop", "color": "red"})
        app.set_listening_state()

# --- WebSocket Server ---

async def handle_websocket(websocket):
    """Handle WebSocket connections from web frontend"""
    websocket_clients.add(websocket)
    
    # Send initial config state
    await websocket.send(json.dumps({
        "type": "config",
        "require_setup": config.get("require_api_key_setup", True),
        "has_key": bool(config.get("api_key"))
    }))
    
    try:
        async for message in websocket:
            data = json.loads(message)
            
            if data.get('action') == 'toggle':
                # Run toggle in main thread
                app.after(0, toggle_listening)
            
            elif data.get('action') == 'save_api_key':
                api_key = data.get('api_key', '').strip()
                if api_key:
                    # Save the API key
                    config['api_key'] = api_key
                    config['require_api_key_setup'] = False
                    if save_config(config):
                        # Reconfigure Gemini with new key
                        if configure_gemini(api_key):
                            await websocket.send(json.dumps({
                                "type": "api_key_response",
                                "success": True,
                                "message": "API key saved successfully!"
                            }))
                        else:
                            await websocket.send(json.dumps({
                                "type": "api_key_response",
                                "success": False,
                                "message": "Invalid API key. Please check and try again."
                            }))
                    else:
                        await websocket.send(json.dumps({
                            "type": "api_key_response",
                            "success": False,
                            "message": "Failed to save API key."
                        }))
                else:
                    await websocket.send(json.dumps({
                        "type": "api_key_response",
                        "success": False,
                        "message": "API key cannot be empty."
                    }))
            
            elif data.get('action') == 'get_config':
                await websocket.send(json.dumps({
                    "type": "config",
                    "require_setup": config.get("require_api_key_setup", True),
                    "has_key": bool(config.get("api_key"))
                }))
    
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        websocket_clients.remove(websocket)

async def start_websocket_server():
    """Start WebSocket server for web frontend communication"""
    async with websockets.serve(handle_websocket, "localhost", 8765):
        await asyncio.Future()  # run forever

def run_websocket_server():
    """Run WebSocket server in separate thread"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_websocket_server())

# --- Main Application Class (Hidden) ---

class BibleAIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bible AI Backend")
        
        # Hide the tkinter window
        self.withdraw()
        
        self.is_speaking = False
        self.animation_id = None
        self.wave_offset = 0
        self.glow_offset = 0
        self.idle_animation_id = None
        
        # Create minimal hidden UI for logging
        self.status_label = tk.Label(self, text="Ready")
        self.log_area = scrolledtext.ScrolledText(self, state=tk.DISABLED)
        self.toggle_button = tk.Button(self, text="Start Listening")
    
    def start_speaking_animation(self):
        """Placeholder for animation"""
        pass
    
    def stop_speaking_animation(self):
        """Placeholder for animation"""
        pass
    
    def set_idle_state(self):
        """Placeholder for state"""
        pass
    
    def set_listening_state(self):
        """Placeholder for state"""
        pass
    
    def set_processing_state(self):
        """Placeholder for state"""
        pass
    
    def set_thinking_state(self):
        """Placeholder for state"""
        pass

def open_web_frontend():
    """Open the web frontend in default browser"""
    html_file = Path(__file__).parent / "web_frontend.html"
    webbrowser.open(f"file://{html_file.absolute()}")

if __name__ == "__main__":
    is_listening = False
    listening_thread = None
    
    # Start WebSocket server in background
    ws_thread = threading.Thread(target=run_websocket_server, daemon=True)
    ws_thread.start()
    
    # Wait a moment for server to start
    time.sleep(0.5)
    
    # Open web frontend
    open_web_frontend()
    
    # Create hidden tkinter app
    app = BibleAIApp()
    
    print("Bible AI Backend running...")
    print("Web UI should open automatically in your browser")
    print("WebSocket server running on ws://localhost:8765")
    
    app.mainloop()
