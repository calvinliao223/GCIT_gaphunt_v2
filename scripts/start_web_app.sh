#!/bin/bash

# Gap Hunter Bot - Web Interface Launcher
# Simple script to start the Streamlit web application

echo "🎓 GAP HUNTER BOT - WEB INTERFACE"
echo "=================================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "💡 Please install Python 3 and try again"
    exit 1
fi

# Check if we're in the right directory (look for web directory)
if [ ! -d "web" ] || [ ! -f "web/streamlit_app.py" ]; then
    echo "❌ web/streamlit_app.py not found!"
    echo "💡 Please run this script from the Gap Hunter Bot project root directory"
    exit 1
fi

# Set up API keys if not already configured
if [ ! -f ".env" ]; then
    echo "🔑 Setting up API keys..."
    python3 scripts/setup_api_keys.py
    echo ""
fi

echo "🚀 Starting Gap Hunter Bot Web Interface..."
echo "🌐 The web app will open at: http://localhost:8501"
echo "🤖 LLM Provider selection available in sidebar"
echo "⚠️  Press Ctrl+C to stop the server"
echo ""

# Launch the web application
python3 web/launch_web_app.py
