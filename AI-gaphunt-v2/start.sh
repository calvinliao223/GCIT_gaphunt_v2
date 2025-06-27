#!/bin/bash

# AI Scientist Easy Starter Script
echo "🤖 AI SCIENTIST - EASY STARTER"
echo "=============================="
echo "🔑 API Keys: Pre-configured"
echo "💻 Mode: CPU-only (no GPU needed)"
echo "📧 Contact: calliaobiz@gmail.com"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ Python not found. Please install Python 3.7+"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "✅ Using: $PYTHON_CMD"
echo ""

# Show options
echo "🎯 CHOOSE YOUR OPTION:"
echo "====================="
echo "1. 💊 Drug Discovery Research (default topic)"
echo "2. 🧪 Quick CPU Test"
echo "3. 📝 Simple Interactive Menu"
echo "4. 🏥 Medical AI Research"
echo ""

read -p "Enter choice (1-4) or press Enter for option 1: " choice

case $choice in
    2)
        echo "🧪 Running Quick CPU Test..."
        $PYTHON_CMD test_cpu_ml.py
        ;;
    3)
        echo "📝 Starting Interactive Menu..."
        $PYTHON_CMD simple_start.py
        ;;
    4)
        echo "🏥 Running Medical AI Research..."
        $PYTHON_CMD -c "
import os
import sys
sys.path.append('.')

# Setup API keys
api_keys = {
    'GOOGLE_API_KEY': 'AIzaSyBdYRBSsPwg7PVuxVdk_rycUhNYdSmTq3E',
    'S2_API_KEY': 'pAnb8EMLQU4KwcV9zyyNC33JvwFtpOvL43PsCRzg',
    'CORE_API_KEY': '94uGwzjrNEOh0TJAod8XH1kcVtSeMyYf',
    'CONTACT_EMAIL': 'calliaobiz@gmail.com',
    'ANTHROPIC_API_KEY': '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',
    'OPENAI_API_KEY': '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',
    'GEMINI_API_KEY': 'AIzaSyBdYRBSsPwg7PVuxVdk_rycUhNYdSmTq3E',
    'TOPIC': 'medical image classification for disease diagnosis'
}

for key, value in api_keys.items():
    os.environ[key] = value

print('🏥 Medical AI Research Starting...')
exec(open('ai_scientist/ideas/i_cant_believe_its_not_betterrealworld.py').read())
"
        ;;
    *)
        echo "💊 Running Drug Discovery Research (default)..."
        $PYTHON_CMD one_click_start.py
        ;;
esac

echo ""
echo "🎉 Done! Thanks for using AI Scientist!"
echo "🔄 Run this script again anytime: ./start.sh"
echo "📧 Questions? Contact: calliaobiz@gmail.com"
