#!/usr/bin/env python3
"""
LLM Provider Demo Script
Demonstrates how to use different LLM providers with Gap Hunter Bot
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

# Load environment variables from .env file
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

# Load environment variables
load_env_file()

from ai_scientist.llm_providers import LLMProviderManager

def demo_provider_selection():
    """Demonstrate provider selection and usage"""
    print("🤖 LLM Provider Demo")
    print("=" * 40)
    
    # Initialize manager
    manager = LLMProviderManager()
    
    # Show available providers
    providers = manager.get_available_providers()
    print(f"📋 Available providers: {', '.join(providers)}")
    
    # Check which providers are available
    available_providers = []
    for provider in providers:
        available = manager.check_provider_availability(provider)
        status = "✅" if available else "❌"
        print(f"   {status} {provider.title()}")
        if available:
            available_providers.append(provider)
    
    if not available_providers:
        print("\n❌ No providers available!")
        print("Please set up API keys using: python scripts/setup_api_keys.py")
        return
    
    print(f"\n🎯 {len(available_providers)} provider(s) ready to use")
    
    # Demonstrate each available provider
    test_prompt = "Explain the concept of machine learning in one sentence."
    system_message = "You are a helpful AI assistant that provides clear, concise explanations."
    
    for provider in available_providers:
        print(f"\n🔄 Testing {provider.title()}...")
        
        try:
            # Get available models for this provider
            models = manager.get_provider_models(provider)
            provider_info = manager.get_provider_info(provider)
            default_model = provider_info.get('default_model', models[0] if models else '')
            
            print(f"   Model: {default_model}")
            
            # Create provider instance
            provider_instance = manager.create_provider(provider, default_model)
            
            # Generate response (with shorter timeout for demo)
            response = provider_instance.generate_response_with_fallback(
                test_prompt, 
                system_message,
                max_retries=1
            )
            
            print(f"   Response: {response[:100]}{'...' if len(response) > 100 else ''}")
            print(f"   ✅ {provider.title()} working correctly")
            
        except Exception as e:
            print(f"   ❌ {provider.title()} failed: {str(e)}")
    
    # Demonstrate fallback functionality
    print(f"\n🔄 Testing fallback functionality...")
    try:
        response, used_provider = manager.generate_with_fallback(
            "What is artificial intelligence?",
            "You are a helpful assistant.",
            preferred_provider=available_providers[0] if available_providers else None
        )
        print(f"   ✅ Fallback successful using {used_provider}")
        print(f"   Response: {response[:100]}{'...' if len(response) > 100 else ''}")
    except Exception as e:
        print(f"   ❌ Fallback failed: {str(e)}")

def demo_configuration():
    """Demonstrate configuration management"""
    print("\n⚙️  Configuration Demo")
    print("=" * 40)
    
    manager = LLMProviderManager()
    
    # Show current preferences
    provider, model = manager.load_user_preferences()
    print(f"📋 Current default: {provider} - {model}")
    
    # Show provider details
    for provider_name in manager.get_available_providers():
        info = manager.get_provider_info(provider_name)
        models = manager.get_provider_models(provider_name)
        available = manager.check_provider_availability(provider_name)
        
        print(f"\n🔧 {info.get('name', provider_name)}:")
        print(f"   Available: {'✅' if available else '❌'}")
        print(f"   Models: {', '.join(models[:3])}{'...' if len(models) > 3 else ''}")
        print(f"   Default: {info.get('default_model', 'N/A')}")
        
        if not available:
            api_key_env = info.get('api_key_env', '')
            if api_key_env:
                print(f"   Required: {api_key_env} environment variable")

def interactive_demo():
    """Interactive demo allowing user to choose provider"""
    print("\n🎮 Interactive Demo")
    print("=" * 40)
    
    manager = LLMProviderManager()
    available_providers = [
        p for p in manager.get_available_providers() 
        if manager.check_provider_availability(p)
    ]
    
    if not available_providers:
        print("❌ No providers available for interactive demo")
        return
    
    print("Available providers:")
    for i, provider in enumerate(available_providers, 1):
        info = manager.get_provider_info(provider)
        print(f"   {i}. {info.get('name', provider.title())}")
    
    try:
        choice = input(f"\nChoose a provider (1-{len(available_providers)}): ").strip()
        choice_idx = int(choice) - 1
        
        if 0 <= choice_idx < len(available_providers):
            selected_provider = available_providers[choice_idx]
            
            # Get user prompt
            user_prompt = input("Enter your question: ").strip()
            if not user_prompt:
                user_prompt = "What are the latest trends in AI research?"
            
            print(f"\n🤖 Using {selected_provider.title()}...")
            
            # Generate response
            response, used_provider = manager.generate_with_fallback(
                user_prompt,
                "You are a knowledgeable AI assistant.",
                preferred_provider=selected_provider
            )
            
            print(f"\n📝 Response from {used_provider.title()}:")
            print("-" * 40)
            print(response)
            print("-" * 40)
            
        else:
            print("❌ Invalid choice")
            
    except (ValueError, KeyboardInterrupt):
        print("\n👋 Demo cancelled")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Main demo function"""
    print("🚀 Gap Hunter Bot - LLM Provider System Demo")
    print("=" * 60)
    
    # Check if any API keys are set
    api_keys = [
        'OPENAI_API_KEY',
        'ANTHROPIC_API_KEY', 
        'GEMINI_API_KEY',
        'GOOGLE_API_KEY'
    ]
    
    keys_set = [key for key in api_keys if os.getenv(key)]
    
    if not keys_set:
        print("⚠️  No API keys detected!")
        print("Please run: python scripts/setup_api_keys.py")
        print("Or set environment variables manually.")
        return
    
    print(f"✅ Found API keys: {', '.join(keys_set)}")
    
    # Run demos
    demo_provider_selection()
    demo_configuration()
    
    # Ask if user wants interactive demo
    try:
        if input("\n🎮 Run interactive demo? (y/N): ").lower().startswith('y'):
            interactive_demo()
    except KeyboardInterrupt:
        pass
    
    print("\n🎉 Demo completed!")
    print("\n💡 Next steps:")
    print("   1. Run the web interface: python web/streamlit_app.py")
    print("   2. Select your preferred provider in the sidebar")
    print("   3. Start hunting for research gaps!")

if __name__ == "__main__":
    main()
