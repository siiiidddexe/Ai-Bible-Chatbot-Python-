#!/bin/bash

# Bible AI - Quick Start Script
# This script sets up and runs the Bible AI chatbot

echo "🌟 Bible AI - Voice-Activated Spiritual Guide"
echo "=============================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.13 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo "✅ All dependencies installed"
echo ""

# Check if config file exists
if [ ! -f "bible_ai_config.json" ]; then
    echo "ℹ️  First time setup detected"
    echo "   You'll be prompted for your Gemini API key in the web UI"
    echo ""
fi

# Start the application
echo "🚀 Starting Bible AI Web Application..."
echo "   Backend: ws://localhost:8765"
echo "   Web UI will open automatically in your browser"
echo ""
echo "Press Ctrl+C to stop the application"
echo "=============================================="
echo ""

python3 bible_ai_with_web.py
