#!/usr/bin/env python3
"""
Test script to validate web interface fixes
"""

import sys
import os
from pathlib import Path

def test_web_interface_imports():
    """Test that web interface can import all required modules"""
    print("🧪 Testing Web Interface Imports")
    print("=" * 40)
    
    # Add project paths
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(project_root / 'AI-gaphunt-v2'))
    sys.path.insert(0, str(project_root / 'web'))
    sys.path.insert(0, str(project_root / 'src'))
    
    # Load environment variables
    env_file = project_root / 'AI-gaphunt-v2' / '.env'
    if env_file.exists():
        print("🔧 Loading .env file...")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    value = value.strip('"\'')
                    if key not in os.environ:
                        os.environ[key] = value
        print("✅ Environment variables loaded")
    else:
        print("⚠️ .env file not found")
    
    # Test core imports
    try:
        print("\n📦 Testing core imports...")
        import streamlit as st
        print("✅ Streamlit imported")
        
        import pandas as pd
        print("✅ Pandas imported")
        
        import yaml
        print("✅ YAML imported")
        
        import plotly.express as px
        print("✅ Plotly imported")
        
    except ImportError as e:
        print(f"❌ Core import failed: {e}")
        return False
    
    # Test Gap Hunter Bot import
    try:
        print("\n🤖 Testing Gap Hunter Bot import...")
        from clean_gap_hunter import GapHunterBot
        print("✅ GapHunterBot imported")
        
        # Test bot initialization
        bot = GapHunterBot()
        print("✅ GapHunterBot initialized")
        
    except ImportError as e:
        print(f"❌ GapHunterBot import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ GapHunterBot initialization failed: {e}")
        return False
    
    # Test LLM Provider Manager import
    try:
        print("\n🧠 Testing LLM Provider Manager import...")
        from ai_scientist.llm_providers import LLMProviderManager
        print("✅ LLMProviderManager imported")
        
    except ImportError as e:
        print(f"⚠️ LLMProviderManager import failed (optional): {e}")
        # This is optional, so don't fail the test
    
    # Test web interface specific functions
    try:
        print("\n🌐 Testing web interface functions...")
        
        # Mock streamlit for testing
        class MockStreamlit:
            class sidebar:
                @staticmethod
                def expander(title):
                    return MockStreamlit()
                @staticmethod
                def write(text):
                    pass
                @staticmethod
                def success(text):
                    pass
                @staticmethod
                def warning(text):
                    pass
            
            def __enter__(self):
                return self
            
            def __exit__(self, *args):
                pass
        
        # Temporarily replace st with mock
        original_st = sys.modules.get('streamlit')
        sys.modules['streamlit'] = MockStreamlit()
        
        # Test the security status function
        sys.path.insert(0, str(project_root / 'web'))
        from streamlit_app import display_simple_security_status
        print("✅ display_simple_security_status imported")
        
        # Restore original streamlit
        if original_st:
            sys.modules['streamlit'] = original_st
        
    except ImportError as e:
        print(f"❌ Web interface function import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Web interface function test failed: {e}")
        return False
    
    print("\n🎉 All imports successful!")
    return True

def test_api_keys():
    """Test that required API keys are available"""
    print("\n🔑 Testing API Keys")
    print("=" * 20)
    
    required_keys = ['S2_API_KEY', 'CORE_API_KEY', 'GOOGLE_API_KEY', 'CONTACT_EMAIL']
    missing_keys = []
    
    for key in required_keys:
        if os.environ.get(key):
            print(f"✅ {key}: Available")
        else:
            print(f"❌ {key}: Missing")
            missing_keys.append(key)
    
    if missing_keys:
        print(f"\n⚠️ Missing keys: {missing_keys}")
        return False
    else:
        print("\n🎉 All API keys available!")
        return True

if __name__ == '__main__':
    print("🧪 Web Interface Fix Validation")
    print("=" * 50)
    
    imports_ok = test_web_interface_imports()
    api_keys_ok = test_api_keys()
    
    if imports_ok and api_keys_ok:
        print("\n✅ Web interface fix validation PASSED!")
        print("🌐 The web interface should now work without NameError")
        sys.exit(0)
    else:
        print("\n❌ Web interface fix validation FAILED!")
        sys.exit(1)
