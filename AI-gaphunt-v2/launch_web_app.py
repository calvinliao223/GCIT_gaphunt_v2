#!/usr/bin/env python3
"""
Launch Script for Gap Hunter Bot Web Interface
Starts the Streamlit web application
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = ['streamlit', 'plotly', 'pyyaml']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Installing missing packages...")
        
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✅ {package} installed successfully")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {package}")
                return False
    
    return True

def setup_environment():
    """Setup environment variables and configuration"""
    print("🎓 GAP HUNTER BOT - WEB INTERFACE")
    print("=" * 50)
    
    # SECURITY: Load API keys from secure configuration only
    # Never hardcode API keys in source code!
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
    try:
        from config_loader import load_env_file_safely, get_api_key

        # Load environment variables from .env file if it exists (development)
        load_env_file_safely()

        # Get API keys securely
        api_keys = {}
        required_keys = ["GOOGLE_API_KEY", "S2_API_KEY", "CORE_API_KEY", "CONTACT_EMAIL"]
        optional_keys = ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"]

        # Set required keys
        for key in required_keys:
            value = get_api_key(key, required=False)
            if value:
                api_keys[key] = value
            else:
                api_keys[key] = ""

        # Set optional LLM provider keys
        for key in optional_keys:
            value = get_api_key(key, required=False)
            api_keys[key] = value if value else ""

    except ImportError:
        print("⚠️ Secure config loader not found, using environment variables directly")
        # Fallback: Get API keys from environment variables
        api_keys = {
            "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY", ""),
            "S2_API_KEY": os.getenv("S2_API_KEY", ""),
            "CORE_API_KEY": os.getenv("CORE_API_KEY", ""),
            "CONTACT_EMAIL": os.getenv("CONTACT_EMAIL", "contact@example.com"),
            "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY", ""),
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
            "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", ""),
        }
    
    for key, value in api_keys.items():
        os.environ[key] = value
    
    print("✅ API keys configured")
    print("✅ Environment ready")

def launch_streamlit():
    """Launch the Streamlit application"""
    print("\n🚀 Launching Gap Hunter Bot Web Interface...")
    print("=" * 50)
    
    # Check if streamlit_app.py exists
    app_file = Path("streamlit_app.py")
    if not app_file.exists():
        print("❌ streamlit_app.py not found!")
        print("💡 Make sure you're running this from the project directory.")
        return False
    
    try:
        # Launch Streamlit
        print("🌐 Starting web server...")
        print("📱 The web interface will open in your browser automatically")
        print("🔗 If it doesn't open, go to: http://localhost:8501")
        print("\n⚠️  To stop the server, press Ctrl+C in this terminal")
        print("=" * 50)
        
        # Open browser after a short delay
        def open_browser():
            time.sleep(3)
            webbrowser.open('http://localhost:8501')
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
        
    except KeyboardInterrupt:
        print("\n\n👋 Gap Hunter Bot web interface stopped!")
        print("Thank you for using Gap Hunter Bot!")
        return True
    except Exception as e:
        print(f"❌ Error launching Streamlit: {e}")
        return False

def main():
    """Main function"""
    try:
        # Check dependencies
        if not check_dependencies():
            print("❌ Failed to install required dependencies")
            return
        
        # Setup environment
        setup_environment()
        
        # Launch Streamlit
        launch_streamlit()
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("💡 This might be a dependency or configuration issue")
        print("📧 Contact: calliaobiz@gmail.com for help")

if __name__ == "__main__":
    main()
