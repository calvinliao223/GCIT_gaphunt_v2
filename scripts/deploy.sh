#!/bin/bash

# Gap Hunter Bot Deployment Script
# Supports multiple deployment targets

set -e

echo "🚀 Gap Hunter Bot Deployment Script"
echo "===================================="

# Configuration
APP_NAME="gaphunter-bot"
DOCKER_IMAGE="gaphunter:latest"

# Functions
deploy_streamlit_cloud() {
    echo "📡 Deploying to Streamlit Cloud..."

    # Security check
    if [ -f ".env" ]; then
        echo "🔐 Security Check: .env file detected"
        if git ls-files --error-unmatch .env 2>/dev/null; then
            echo "❌ SECURITY RISK: .env file is tracked by git!"
            echo "Run: git rm --cached .env && git commit -m 'Remove .env from tracking'"
            exit 1
        else
            echo "✅ .env file is properly ignored"
        fi
    fi

    echo ""
    echo "📋 Deployment Steps:"
    echo "1. Ensure .env is in .gitignore (✅ verified)"
    echo "2. Push your code to GitHub"
    echo "3. Go to https://share.streamlit.io/"
    echo "4. Connect your repository"
    echo "5. Set main file: web/streamlit_app.py"
    echo "6. 🔑 CRITICAL: Add API keys in Secrets (TOML format)"
    echo ""
    echo "📖 See docs/SECURE_DEPLOYMENT.md for detailed instructions"

    read -p "Press Enter when ready to continue..."
}

deploy_heroku() {
    echo "🔧 Deploying to Heroku..."
    
    # Check if Heroku CLI is installed
    if ! command -v heroku &> /dev/null; then
        echo "❌ Heroku CLI not found. Install from: https://devcenter.heroku.com/articles/heroku-cli"
        exit 1
    fi
    
    # Create Heroku app
    echo "Creating Heroku app..."
    heroku create $APP_NAME --region us
    
    # Set environment variables
    echo "Setting environment variables..."
    heroku config:set OPENAI_API_KEY="$OPENAI_API_KEY" --app $APP_NAME
    heroku config:set ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" --app $APP_NAME
    heroku config:set GEMINI_API_KEY="$GEMINI_API_KEY" --app $APP_NAME
    heroku config:set GOOGLE_API_KEY="$GOOGLE_API_KEY" --app $APP_NAME
    heroku config:set S2_API_KEY="$S2_API_KEY" --app $APP_NAME
    heroku config:set CORE_API_KEY="$CORE_API_KEY" --app $APP_NAME
    heroku config:set CONTACT_EMAIL="$CONTACT_EMAIL" --app $APP_NAME
    
    # Deploy
    git add .
    git commit -m "Deploy to Heroku" || true
    git push heroku main
    
    echo "✅ Deployed to: https://$APP_NAME.herokuapp.com"
}

deploy_docker() {
    echo "🐳 Building Docker image..."
    
    # Build image
    docker build -f docker/Dockerfile -t $DOCKER_IMAGE .
    
    # Run container
    echo "🚀 Starting container..."
    docker run -d \
        --name $APP_NAME \
        -p 8501:8501 \
        -e OPENAI_API_KEY="$OPENAI_API_KEY" \
        -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
        -e GEMINI_API_KEY="$GEMINI_API_KEY" \
        -e GOOGLE_API_KEY="$GOOGLE_API_KEY" \
        -e S2_API_KEY="$S2_API_KEY" \
        -e CORE_API_KEY="$CORE_API_KEY" \
        -e CONTACT_EMAIL="$CONTACT_EMAIL" \
        $DOCKER_IMAGE
    
    echo "✅ Container running at: http://localhost:8501"
}

deploy_vps() {
    echo "🖥️  VPS Deployment Instructions:"
    echo "1. Copy files to your VPS"
    echo "2. Install Docker and Docker Compose"
    echo "3. Set up environment variables in .env file"
    echo "4. Run: docker-compose -f docker/docker-compose.yml up -d"
    echo "5. Configure reverse proxy (nginx) for custom domain"
    echo "6. Set up SSL certificate (Let's Encrypt)"
}

# Main menu
echo ""
echo "Choose deployment option:"
echo "1. Streamlit Cloud (Free, easiest)"
echo "2. Heroku (Free tier available)"
echo "3. Docker (Local/VPS)"
echo "4. VPS Instructions"
echo "5. Exit"
echo ""

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        deploy_streamlit_cloud
        ;;
    2)
        deploy_heroku
        ;;
    3)
        deploy_docker
        ;;
    4)
        deploy_vps
        ;;
    5)
        echo "👋 Deployment cancelled"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "🎉 Deployment process completed!"
echo "💡 Don't forget to set up your API keys in the deployment environment"
