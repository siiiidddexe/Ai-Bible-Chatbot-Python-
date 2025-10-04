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
import subprocess
import signal
warnings.filterwarnings('ignore')

import tkinter as tk
from tkinter import scrolledtext
import google.generativeai as genai
import speech_recognition as sr

# Restore stderr after all imports are complete
sys.stderr.close()
sys.stderr = _original_stderr

# --- Configuration ---
# 🚨 PASTE YOUR NEW, PRIVATE GEMINI API KEY HERE
# 🚨 DO NOT SHARE THIS KEY WITH ANYONE
YOUR_API_KEY = "" 

# Configure the Gemini API client
try:
    genai.configure(api_key=YOUR_API_KEY)
except Exception as e:
    print(f"API Key configuration failed: {e}")

# Set up the Gemini model with a specific persona (system instruction)
# Using gemini-2.5-flash - the latest stable Gemini model
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

# --- Core Functions ---

say_process = None  # Store the current say process

def speak(text):
    """Uses macOS's built-in 'say' command to speak text aloud with animation."""
    update_status("Speaking...")
    app.is_speaking = True
    app.start_speaking_animation()
    
    # Update button to show 'Stop Speaking'
    app.toggle_button.config(text="Stop Speaking", bg="#ff4757", activebackground="#ee3344", fg="#ffffff")
    
    # Write text to a temporary file to avoid shell escaping issues with long text
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(text)
        temp_file = f.name
    
    try:
        # Use -f flag to read from file instead of passing text directly
        os.system(f"say -f {temp_file}")
    finally:
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
        update_status("Listening for 'Hey Bible'...")

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
                update_status("Listening for 'Hey Bible'...")
                app.set_listening_state()
                
                audio_wake_word = recognizer.listen(source, phrase_time_limit=10)
            
            text = recognizer.recognize_google(audio_wake_word).lower()
            log_message(f"Heard: {text}")

            if "hey bible" in text:
                update_status("Wake word detected. Listening for your command...")
                app.set_processing_state()
                speak("Yes, how can I help?")
                
                # Wait for the prompt after wake word
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    update_status("Listening for command...")
                    audio_command = recognizer.listen(source, timeout=5, phrase_time_limit=15)
                
                prompt = recognizer.recognize_google(audio_command)
                log_message(f"User Prompt: {prompt}")

                update_status("Thinking...")
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

def update_status(message):
    app.status_label.config(text=message)

def log_message(message):
    app.log_area.config(state=tk.NORMAL)
    app.log_area.insert(tk.END, message + "\n")
    app.log_area.see(tk.END)
    app.log_area.config(state=tk.DISABLED)

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
        update_status("Listening for 'Hey Bible'...")
        app.status_label.config(fg="#10b981")
        return
    
    # If listening, stop it
    if is_listening:
        is_listening = False
        app.toggle_button.config(text="Start Listening", bg="#6366f1", activebackground="#5b5ff1", fg="#f0f0f0")
        update_status("Ready")
        app.status_label.config(fg="#9ca3af")
        log_message("--- AI Deactivated ---\n")
        app.set_idle_state()
    else:
        # Start listening
        is_listening = True
        listening_thread = threading.Thread(target=listen_and_process, daemon=True)
        listening_thread.start()
        app.toggle_button.config(text="Stop", bg="#ff4757", activebackground="#ee3344", fg="#ffffff")
        log_message("--- AI Activated ---")
        update_status("Listening...")
        app.status_label.config(fg="#10b981")
        app.set_listening_state()

# --- Main Application Class ---

class BibleAIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bible AI")
        self.geometry("1100x950")
        self.minsize(900, 800)
        
        # Ultra-premium gradient background
        self.configure(bg="#0a0118")
        
        self.is_speaking = False
        self.animation_id = None
        self.wave_offset = 0
        self.glow_offset = 0
        self.idle_animation_id = None
        self.button_hover = False
        
        # Main container - centered design
        main_container = tk.Frame(self, bg="#0a0118")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Spacer for vertical centering
        tk.Frame(main_container, bg="#0a0118", height=50).pack()
        
        # Title - Minimal and elegant with letter spacing effect
        title = tk.Label(
            main_container, 
            text="B i b l e  A I", 
            font=("Helvetica Neue", 52, "bold"),
            bg="#0a0118",
            fg="#ffffff"
        )
        title.pack(pady=(0, 8))
        
        # Subtitle - Ultra subtle with better spacing
        subtitle = tk.Label(
            main_container,
            text="Voice-Activated Spiritual Guide",
            font=("Helvetica Neue", 14),
            bg="#0a0118",
            fg="#6b7280"
        )
        subtitle.pack(pady=(0, 35))
        
        # Orb section - Main focal point
        orb_section = tk.Frame(main_container, bg="#0a0118")
        orb_section.pack(pady=25)
        
        # Canvas for ultra-smooth animated orb with responsive size
        self.canvas = tk.Canvas(
            orb_section, 
            width=500, 
            height=500, 
            bg="#0a0118",
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Draw initial orb
        self.orb = None
        self.wave_lines = []
        self.draw_orb()
        
        # Status text - Minimal, centered with better contrast
        self.status_label = tk.Label(
            main_container, 
            text="Ready", 
            font=("Helvetica Neue", 16),
            bg="#0a0118",
            fg="#9ca3af"
        )
        self.status_label.pack(pady=(25, 20))
        
        # Single smart button with shadow effect
        button_frame = tk.Frame(main_container, bg="#0a0118")
        button_frame.pack()
        
        self.toggle_button = tk.Button(
            button_frame,
            text="Start Listening",
            command=toggle_listening,
            font=("Helvetica Neue", 16, "bold"),
            bg="#6366f1",
            fg="#f0f0f0",
            activebackground="#5b5ff1",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            bd=0,
            padx=65,
            pady=22,
            cursor="hand2",
            disabledforeground="#ffffff"
        )
        self.toggle_button.pack()
        
        # Bind hover effects
        self.toggle_button.bind("<Enter>", self.on_button_hover)
        self.toggle_button.bind("<Leave>", self.on_button_leave)
        
        # Hint - Ultra subtle with icon
        hint = tk.Label(
            main_container,
            text='💬 Say "Hey Bible" to activate',
            font=("Helvetica Neue", 13),
            bg="#0a0118",
            fg="#4b5563"
        )
        hint.pack(pady=(18, 0))
        
        # Spacer
        tk.Frame(main_container, bg="#0a0118", height=25).pack()
        
        # Log section - Minimalist with subtle border
        log_section = tk.Frame(main_container, bg="#0a0118")
        log_section.pack(fill=tk.BOTH, expand=True, padx=70, pady=(0, 35))
        
        # Log container with subtle background and rounded effect
        log_container = tk.Frame(log_section, bg="#1a1a2e", highlightbackground="#2a2a4a", highlightthickness=1)
        log_container.pack(fill=tk.BOTH, expand=True)
        
        self.log_area = scrolledtext.ScrolledText(
            log_container,
            state=tk.DISABLED,
            wrap=tk.WORD,
            height=5,
            width=90,
            bg="#1a1a2e",
            fg="#a1a1aa",
            font=("Monaco", 11),
            insertbackground="#5b6cf6",
            bd=0,
            padx=22,
            pady=18,
            selectbackground="#2d2d44",
            selectforeground="#ffffff"
        )
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
    
    def draw_orb(self, pulse_offset=0):
        """Draw ultra-smooth gradient orb as perfect glass sphere with subtle breathing"""
        self.canvas.delete("all")
        center_x, center_y = 250, 250
        
        # More noticeable breathing effect
        breath = 8 * math.sin(pulse_offset)  # Increased from 3 to 8
        
        # Outer atmospheric glow - deep purple haze
        for i in range(35, 0, -1):
            radius = 165 + i * 4 + breath * 0.5  # Increased multiplier
            ratio = i / 35
            color = self.blend_color("#1a1540", "#2a2055", ratio)
            self.canvas.create_oval(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                fill=color, outline="", stipple="gray12"
            )
        
        # Mid-layer glow
        for i in range(20, 0, -1):
            radius = 150 + i * 2.5 + breath * 0.8  # Increased multiplier
            ratio = i / 20
            color = self.blend_color("#2d2560", "#3d3580", ratio)
            self.canvas.create_oval(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                fill=color, outline="", stipple="gray25"
            )
        
        # Main sphere - smooth gradient from purple to cyan
        base_radius = 140
        for i in range(35, 0, -1):
            radius = base_radius - i * 3.8 + breath  # More visible pulse
            ratio = i / 35
            
            # Perfect gradient: purple -> indigo -> blue -> cyan
            if ratio > 0.75:
                color = self.blend_color("#7dd3fc", "#a5f3fc", (ratio - 0.75) / 0.25)
            elif ratio > 0.5:
                color = self.blend_color("#60a5fa", "#7dd3fc", (ratio - 0.5) / 0.25)
            elif ratio > 0.25:
                color = self.blend_color("#6366f1", "#60a5fa", (ratio - 0.25) / 0.25)
            else:
                color = self.blend_color("#7c3aed", "#6366f1", ratio / 0.25)
            
            self.canvas.create_oval(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                fill=color, outline=""
            )
        
        # Glass highlight - top left for 3D sphere effect
        highlight_radius = 100
        self.canvas.create_oval(
            center_x - highlight_radius, center_y - highlight_radius,
            center_x - 15, center_y - 15,
            fill="#e0f2fe", outline="", stipple="gray12"
        )
        
        # Secondary subtle highlight
        self.canvas.create_oval(
            center_x - 80, center_y - 80,
            center_x - 30, center_y - 30,
            fill="#f0f9ff", outline="", stipple="gray12"
        )
        
        # Sparkle icons with more noticeable floating
        sparkle_float = 4 * math.sin(pulse_offset * 0.9)  # Increased amplitude and speed
        sparkle_positions = [
            (center_x, center_y - 28 + sparkle_float, "✦", 40),
            (center_x - 33, center_y + 20 - sparkle_float * 0.6, "✦", 23),
            (center_x + 33, center_y + 15 + sparkle_float * 0.4, "✦", 19)
        ]
        
        for x, y, symbol, size in sparkle_positions:
            self.canvas.create_text(
                x, y,
                text=symbol,
                font=("Helvetica", size),
                fill="#ffffff"
            )
        
        # Store orb reference
        self.orb = self.canvas.create_oval(
            center_x - 140, center_y - 140,
            center_x + 140, center_y + 140,
            fill="", outline=""
        )
    
    def blend_color(self, color1, color2, ratio):
        """Blend two hex colors"""
        c1 = tuple(int(color1[i:i+2], 16) for i in (1, 3, 5))
        c2 = tuple(int(color2[i:i+2], 16) for i in (1, 3, 5))
        blended = tuple(int(c1[i] + (c2[i] - c1[i]) * ratio) for i in range(3))
        return f"#{blended[0]:02x}{blended[1]:02x}{blended[2]:02x}"
    
    def animate_waves(self):
        """Slower, more elegant speaking animation"""
        if not self.is_speaking:
            return
        
        self.canvas.delete("all")
        center_x, center_y = 250, 250
        self.wave_offset += 0.06  # Slower animation
        self.glow_offset += 0.04
        
        # Outer ripple rings - slow elegant waves
        for i in range(8):
            phase = self.glow_offset + i * 0.5
            radius = 180 + 28 * math.sin(phase)
            
            color = self.blend_color("#4f46e5", "#818cf8", i / 8)
            width = int(2 + 1.5 * math.sin(phase))
            self.canvas.create_oval(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                fill="", outline=color, width=width, stipple="gray25"
            )
        
        # Main pulsing sphere - gentle breathing
        pulse = 140 + 12 * math.sin(self.wave_offset * 1.2)
        
        for i in range(35, 0, -1):
            radius = pulse - i * 3.8
            ratio = i / 35
            
            # Smooth gradient shift
            if ratio > 0.75:
                color = self.blend_color("#a5f3fc", "#dbeafe", (ratio - 0.75) / 0.25)
            elif ratio > 0.5:
                color = self.blend_color("#7dd3fc", "#a5f3fc", (ratio - 0.5) / 0.25)
            elif ratio > 0.25:
                color = self.blend_color("#60a5fa", "#7dd3fc", (ratio - 0.25) / 0.25)
            else:
                color = self.blend_color("#818cf8", "#60a5fa", ratio / 0.25)
            
            self.canvas.create_oval(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                fill=color, outline=""
            )
        
        # Slower rotating particles
        for j in range(10):
            angle = self.wave_offset * 0.9 + j * (2 * math.pi / 10)
            particle_dist = 115 + 15 * math.sin(self.wave_offset + j * 0.4)
            particle_x = center_x + particle_dist * math.cos(angle)
            particle_y = center_y + particle_dist * math.sin(angle)
            particle_size = 2 + 1.5 * math.sin(self.wave_offset * 1.3 + j)
            
            # Particle glow
            self.canvas.create_oval(
                particle_x - particle_size - 1, particle_y - particle_size - 1,
                particle_x + particle_size + 1, particle_y + particle_size + 1,
                fill="#e0f2fe", outline=""
            )
            self.canvas.create_oval(
                particle_x - particle_size, particle_y - particle_size,
                particle_x + particle_size, particle_y + particle_size,
                fill="#ffffff", outline=""
            )
        
        # Gentle floating sparkles
        sparkle_offset = self.wave_offset * 1.1
        sparkle_positions = [
            (center_x + 10 * math.sin(sparkle_offset), center_y - 28, "✦", 36),
            (center_x - 33, center_y + 20 + 5 * math.sin(sparkle_offset + 1.8), "✦", 21),
            (center_x + 33, center_y + 15 + 5 * math.sin(sparkle_offset + 3.2), "✦", 17)
        ]
        
        for x, y, symbol, size in sparkle_positions:
            self.canvas.create_text(
                x, y,
                text=symbol,
                font=("Helvetica", size),
                fill="#ffffff"
            )
        
        self.animation_id = self.after(40, self.animate_waves)  # Slower frame rate
    
    def hsv_to_rgb(self, h, s, v):
        """Convert HSV to RGB hex color"""
        import colorsys
        r, g, b = colorsys.hsv_to_rgb(h/360, s, v)
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
    
    def start_idle_animation(self):
        """Faster, more noticeable breathing animation when idle"""
        if self.is_speaking:
            return
        
        if not hasattr(self, 'idle_breath_offset'):
            self.idle_breath_offset = 0
        
        self.idle_breath_offset += 0.10  # Faster increment (was 0.03)
        self.draw_orb(self.idle_breath_offset)
        
        # Faster animation rate - 30 FPS instead of 20
        self.idle_animation_id = self.after(33, self.start_idle_animation)
    
    def start_speaking_animation(self):
        """Start the speaking animation"""
        if self.idle_animation_id:
            self.after_cancel(self.idle_animation_id)
            self.idle_animation_id = None
        if self.animation_id:
            self.after_cancel(self.animation_id)
        self.animate_waves()
    
    def stop_speaking_animation(self):
        """Stop the animation and return to idle state"""
        if self.animation_id:
            self.after_cancel(self.animation_id)
            self.animation_id = None
        if not hasattr(self, 'idle_breath_offset'):
            self.idle_breath_offset = 0
        self.draw_orb(self.idle_breath_offset)
        self.start_idle_animation()
    
    def on_button_hover(self, event):
        """Button hover effect"""
        if self.toggle_button['text'] == "Start Listening":
            self.toggle_button.config(bg="#7c8cf6")
        else:
            self.toggle_button.config(bg="#ff5767")
    
    def on_button_leave(self, event):
        """Button leave effect"""
        if self.toggle_button['text'] == "Start Listening":
            self.toggle_button.config(bg="#6366f1")
        else:
            self.toggle_button.config(bg="#ff4757")
    
    def set_idle_state(self):
        """Visual state when idle"""
        if not hasattr(self, 'idle_breath_offset'):
            self.idle_breath_offset = 0
        self.draw_orb(self.idle_breath_offset)
        self.start_idle_animation()
    
    def set_listening_state(self):
        """Visual state when listening"""
        pass  # Orb stays same, button changes
    
    def set_processing_state(self):
        """Visual state when processing"""
        pass  # Orb stays same
    
    def set_thinking_state(self):
        """Visual state when AI is thinking"""
        pass  # Orb stays same

if __name__ == "__main__":
    is_listening = False
    listening_thread = None
    
    app = BibleAIApp()
    app.mainloop()