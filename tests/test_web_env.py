#!/usr/bin/env python3
"""
Test environment variable loading in web context
"""

import os
import sys
from pathlib import Path

# Add paths like the web app does
sys.path.append('.')
sys.path.append('src')
sys.path.append('scripts')

def load_env_file():
    """Load environment variables from .env file"""
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    # Remove quotes if present
                    value = value.strip('"\'')
                    os.environ[key] = value
        return True
    return False

def test_environment():
    """Test environment variable loading"""
    print("🧪 Testing Environment Variable Loading")
    print("=" * 50)
    
    # Load environment variables
    env_loaded = load_env_file()
    print(f"📁 .env file loaded: {'✅' if env_loaded else '❌'}")
    
    # Check API keys
    api_keys = [
        'OPENAI_API_KEY',
        'ANTHROPIC_API_KEY', 
        'GEMINI_API_KEY',
        'GOOGLE_API_KEY'
    ]
    
    print("\n🔑 API Key Status:")
    for key in api_keys:
        value = os.getenv(key)
        status = "✅ Set" if value else "❌ Not set"
        print(f"   {key}: {status}")
        if value:
            print(f"      Value: {value[:10]}...{value[-4:] if len(value) > 14 else value}")
    
    # Test LLM Provider Manager
    try:
        from ai_scientist.llm_providers import LLMProviderManager
        
        # Use absolute path like the web app
        config_path = Path(__file__).parent.parent / "config" / "bfts_config.yaml"
        manager = LLMProviderManager(str(config_path))
        
        print(f"\n🤖 LLM Provider Manager initialized: ✅")
        print(f"📋 Config file: {config_path}")
        print(f"📋 Config exists: {'✅' if config_path.exists() else '❌'}")
        
        # Test provider availability
        providers = manager.get_available_providers()
        print(f"\n🔍 Provider Availability:")
        for provider in providers:
            available = manager.check_provider_availability(provider)
            status = "✅ Available" if available else "❌ Unavailable"
            print(f"   {provider.title()}: {status}")
            
            if not available:
                info = manager.get_provider_info(provider)
                api_key_env = info.get('api_key_env', '')
                if api_key_env:
                    key_status = "Set" if os.getenv(api_key_env) else "Not set"
                    print(f"      Required: {api_key_env} ({key_status})")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM Provider Manager failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_environment()
    
    if success:
        print("\n✅ Environment test passed!")
        print("💡 Web interface should show providers as available")
    else:
        print("\n❌ Environment test failed!")
        print("💡 Check the error messages above")
