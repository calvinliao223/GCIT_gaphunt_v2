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

# Setup API keys from secure configuration
# SECURITY: Never hardcode API keys in source code!
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
try:
    from config_loader import load_env_file_safely, get_api_key

    # Load environment variables from .env file if it exists (development)
    load_env_file_safely()

    # Get API keys securely
    required_keys = ['GOOGLE_API_KEY', 'S2_API_KEY', 'CORE_API_KEY', 'CONTACT_EMAIL']
    optional_keys = ['ANTHROPIC_API_KEY', 'OPENAI_API_KEY', 'GEMINI_API_KEY']

    # Set required keys
    for key in required_keys:
        value = get_api_key(key, required=False)
        if value:
            os.environ[key] = value

    # Set optional LLM provider keys
    for key in optional_keys:
        value = get_api_key(key, required=False)
        if value:
            os.environ[key] = value

    # Set default topic if not provided
    if not os.environ.get('TOPIC'):
        os.environ['TOPIC'] = 'medical image classification for disease diagnosis'

except ImportError:
    print("⚠️ Secure config loader not found")
    print("💡 Please ensure API keys are set as environment variables")
    print("📖 See .env.example for the required format")

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
