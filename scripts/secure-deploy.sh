#!/bin/bash

# Secure Deployment Script - Removes hardcoded keys and deploys safely
set -e

echo "🔐 Secure Deployment Process"
echo "============================"

# Step 1: Security validation
echo "🔍 Step 1: Security validation..."

# Check if .env is properly ignored
if git ls-files --error-unmatch .env 2>/dev/null; then
    echo "❌ CRITICAL: .env file is tracked by git!"
    echo "Run: git rm --cached .env && git commit -m 'Remove .env from tracking'"
    exit 1
fi

# Check for hardcoded API keys in source code (excluding .env file)
echo "Scanning for hardcoded LLM API keys in source code..."
if grep -r "sk-proj-[a-zA-Z0-9]" . --exclude-dir=.git --exclude="*.md" --exclude="*.example" --exclude-dir=.venv --exclude=".env" 2>/dev/null; then
    echo "❌ OpenAI API keys found in source code!"
    exit 1
fi

if grep -r "sk-ant-api[0-9]" . --exclude-dir=.git --exclude="*.md" --exclude="*.example" --exclude-dir=.venv --exclude=".env" 2>/dev/null; then
    echo "❌ Anthropic API keys found in source code!"
    exit 1
fi

echo "✅ No hardcoded LLM API keys detected"

# Step 2: Clean up
echo "🧹 Step 2: Cleaning up..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
echo "✅ Cache files cleaned"

# Step 3: Commit changes
echo "📝 Step 3: Committing secure changes..."
git add .
git status

read -p "Commit these changes? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git commit -m "🔐 Remove hardcoded API keys and implement secure configuration"
    echo "✅ Changes committed"
else
    echo "⚠️ Changes not committed"
fi

# Step 4: Push to GitHub
read -p "Push to GitHub? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git push origin main
    echo "✅ Pushed to GitHub"
else
    echo "⚠️ Not pushed to GitHub"
fi

# Step 5: Deployment instructions
echo ""
echo "🚀 Step 5: Deployment Instructions"
echo "=================================="
echo ""
echo "Your code is now secure! Choose your deployment method:"
echo ""
echo "1. 🌐 Streamlit Cloud (Recommended):"
echo "   - Go to https://share.streamlit.io"
echo "   - Connect your GitHub repository"
echo "   - Set main file: web/streamlit_app.py"
echo "   - Add your API keys in Secrets (TOML format)"
echo ""
echo "2. 🐳 Docker/Kubernetes:"
echo "   - Use: ./devops/deploy-with-secrets.sh"
echo "   - Your API keys will be managed securely"
echo ""
echo "3. ☁️ Cloud Platforms (Heroku, AWS, etc.):"
echo "   - Set environment variables in your platform"
echo "   - Deploy using platform-specific methods"
echo ""
echo "📖 See docs/SECURE_DEPLOYMENT.md for detailed instructions"
echo ""
echo "🔐 Your API keys are now incognito and secure! 🕵️‍♂️"
