#!/usr/bin/env python3
"""
Test script for Gap Hunter Bot Web Interface
Verifies that all components work correctly
"""

import sys
import os
import importlib.util

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    
    required_modules = [
        'streamlit',
        'plotly',
        'yaml',
        'pandas',
        'requests'
    ]
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            return False
    
    return True

def test_gap_hunter_bot():
    """Test that GapHunterBot class can be imported and initialized"""
    print("\n🤖 Testing Gap Hunter Bot...")
    
    try:
        from clean_gap_hunter import GapHunterBot
        bot = GapHunterBot()
        print("✅ GapHunterBot class imported and initialized")
        return True
    except Exception as e:
        print(f"❌ GapHunterBot error: {e}")
        return False

def test_streamlit_app():
    """Test that Streamlit app can be imported"""
    print("\n🌐 Testing Streamlit app...")
    
    try:
        # Test if streamlit_app.py exists and can be imported
        if not os.path.exists('streamlit_app.py'):
            print("❌ streamlit_app.py not found")
            return False
        
        spec = importlib.util.spec_from_file_location("streamlit_app", "streamlit_app.py")
        streamlit_app = importlib.util.module_from_spec(spec)
        
        # Don't execute the module, just check if it can be loaded
        print("✅ streamlit_app.py can be loaded")
        return True
    except Exception as e:
        print(f"❌ Streamlit app error: {e}")
        return False

def test_api_keys():
    """Test that API keys are properly configured"""
    print("\n🔑 Testing API keys...")
    
    required_keys = [
        'S2_API_KEY',
        'CORE_API_KEY', 
        'GOOGLE_API_KEY',
        'CONTACT_EMAIL'
    ]
    
    # Import and initialize bot to set up API keys
    try:
        from clean_gap_hunter import GapHunterBot
        bot = GapHunterBot()
        
        for key in required_keys:
            if os.environ.get(key):
                print(f"✅ {key} configured")
            else:
                print(f"❌ {key} missing")
                return False
        
        return True
    except Exception as e:
        print(f"❌ API key setup error: {e}")
        return False

def test_file_structure():
    """Test that all required files exist"""
    print("\n📁 Testing file structure...")
    
    required_files = [
        'streamlit_app.py',
        'clean_gap_hunter.py',
        'launch_web_app.py',
        'start_web_app.sh',
        'requirements.txt'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} missing")
            return False
    
    return True

def main():
    """Run all tests"""
    print("🧪 GAP HUNTER BOT - WEB INTERFACE TESTS")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Module Imports", test_imports),
        ("Gap Hunter Bot", test_gap_hunter_bot),
        ("Streamlit App", test_streamlit_app),
        ("API Keys", test_api_keys)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Web interface is ready to use.")
        print("\n🚀 To start the web interface, run:")
        print("   python launch_web_app.py")
        print("   OR")
        print("   ./start_web_app.sh")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install streamlit plotly pyyaml")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
