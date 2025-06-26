#!/usr/bin/env python3
"""
Setup script to configure API keys for AI Scientist
"""

import os
import json
from pathlib import Path

def setup_api_keys():
    """Set up API keys as environment variables"""
    
    # Your API keys
    api_keys = {
        # Google API Key (Required)
        "GOOGLE_API_KEY": "AIzaSyBdYRBSsPwg7PVuxVdk_rycUhNYdSmTq3E",
        
        # Semantic Scholar API Key (Recommended)
        "S2_API_KEY": "pAnb8EMLQU4KwcV9zyyNC33JvwFtpOvL43PsCRzg",
        
        # CORE API Key (Recommended)
        "CORE_API_KEY": "94uGwzjrNEOh0TJAod8XH1kcVtSeMyYf",
        
        # Contact email for polite API access
        "CONTACT_EMAIL": "calliaobiz@gmail.com",
        
        # Anthropic API Key
        "ANTHROPIC_API_KEY": "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",
        
        # OpenAI API Key
        "OPENAI_API_KEY": "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",
        
        # Gemini API Key (using Google API Key)
        "GEMINI_API_KEY": "AIzaSyBdYRBSsPwg7PVuxVdk_rycUhNYdSmTq3E",
    }
    
    # Set environment variables
    for key, value in api_keys.items():
        os.environ[key] = value
        print(f"✅ Set {key}")
    
    # Save to .env file for persistence
    env_file = Path(".env")
    with open(env_file, "w") as f:
        f.write("# AI Scientist API Keys\n")
        f.write("# Generated automatically - do not share this file!\n\n")
        for key, value in api_keys.items():
            f.write(f'{key}="{value}"\n')
    
    print(f"\n✅ API keys saved to {env_file}")
    print("🔒 Keep this file secure and don't share it!")
    
    return api_keys

def load_env_file():
    """Load environment variables from .env file"""
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    # Remove quotes if present
                    value = value.strip('"\'')
                    os.environ[key] = value
        print("✅ Loaded API keys from .env file")
        return True
    return False

def verify_api_keys():
    """Verify that all required API keys are set"""
    required_keys = [
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY", 
        "GOOGLE_API_KEY"
    ]
    
    missing_keys = []
    for key in required_keys:
        if not os.getenv(key):
            missing_keys.append(key)
    
    if missing_keys:
        print(f"❌ Missing API keys: {', '.join(missing_keys)}")
        return False
    else:
        print("✅ All required API keys are set")
        return True

if __name__ == "__main__":
    print("🔑 Setting up AI Scientist API Keys")
    print("=" * 40)
    
    # Try to load existing .env file first
    if not load_env_file():
        # If no .env file, set up new keys
        setup_api_keys()
    
    # Verify all keys are present
    verify_api_keys()
    
    print("\n🚀 Ready to run AI Scientist!")
